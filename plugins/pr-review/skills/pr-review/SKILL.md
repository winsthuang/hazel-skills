---
name: pr-review
description: "Use this skill when the user asks to review a PR, check a pull request, or mentions
  /pr-review. Reviews for bugs, CLAUDE.md compliance, AND whether the PR reveals patterns that
  should be added to CLAUDE.md."
---

Review a pull request for bugs, CLAUDE.md compliance, and — critically — whether the PR reveals
patterns, conventions, or learnings that should be documented back into CLAUDE.md.

Most review tools check if code follows CLAUDE.md. This one also asks: **"Does this PR teach us
something that CLAUDE.md doesn't yet capture?"**

## Arguments

- `$ARGUMENTS`:
  - A PR number or URL — review that PR
  - `--comment` — post findings as inline GitHub comments
  - *(empty)* — detect the current branch's open PR

## Execution Model

This skill adapts to available capabilities. Try each tier in order — use the first one that works.

### Tier 1: Team agents (split panes)

If `TeamCreate` is available, create a team and spawn agents with `team_name` for split-pane UI.

### Tier 2: Parallel subagents

If `TeamCreate` is not available but `Agent` tool is, spawn agents in parallel as background
subagents (no split panes, but still parallel).

### Tier 3: Sequential (single agent)

If neither is available, run all review steps sequentially in the current context. This is slower
but works everywhere.

---

## Step 1: Gather Context

1. Identify the PR (from argument, or detect via `gh pr view --json number,title,body,headRefName`).
2. If the PR is closed, draft, or trivial (e.g., automated dependency bumps), stop:
   > "PR #N is [closed/draft/trivial] — skipping review."
3. Fetch the diff: `gh pr diff <PR>`
4. Fetch PR title, description, and changed file list: `gh pr view <PR> --json title,body,files`
5. Find all relevant CLAUDE.md files:
   - Root `CLAUDE.md`
   - Any `CLAUDE.md` in directories containing changed files (walk up to repo root)
   - Read each one into context

## Step 2: Launch Review Agents

Spawn these agents (in parallel if using Tier 1 or 2, sequentially if Tier 3):

### Agent 1: Bug Scanner

**Model preference:** opus (if available), otherwise sonnet

Prompt:
> Review this PR diff for bugs. Focus ONLY on the changed code — do not speculate about
> code you cannot see. Flag only issues where:
> - Code will fail to compile/parse (syntax errors, missing imports, type errors)
> - Code will produce wrong results regardless of inputs (clear logic errors)
> - Security vulnerabilities in the changed code
>
> Do NOT flag: style issues, potential issues dependent on specific inputs, nitpicks,
> or anything a linter would catch. If you're not certain, don't flag it.
>
> For each issue, return: file, line range, description, severity (high/medium).

### Agent 2: CLAUDE.md Compliance

**Model preference:** sonnet

Prompt:
> Check if the changed code violates any rules in the CLAUDE.md files provided.
> Only flag clear, unambiguous violations where you can quote the exact rule being broken.
> Ignore rules that don't apply to the changed files' directories.
>
> For each violation: file, line range, the CLAUDE.md rule (quoted), how it's violated.

### Agent 3: CLAUDE.md Update Detector

**Model preference:** sonnet

This is the novel agent. Prompt:
> You are reviewing a PR to determine if it reveals patterns, conventions, decisions, or
> gotchas that should be documented in CLAUDE.md but currently aren't.
>
> Look for:
> - **New conventions** the PR establishes (naming patterns, file organization, API patterns)
> - **Non-obvious decisions** evident in the code (why something was done a certain way)
> - **Gotchas discovered** (workarounds, edge cases, things that broke and were fixed)
> - **Dependency/tooling changes** that affect how others should write code
> - **New architectural patterns** (new abstractions, service boundaries, data flow)
>
> Cross-reference against the existing CLAUDE.md files. Only suggest additions for things
> that are genuinely NOT already documented and would help the next developer.
>
> For each suggestion, return:
> - Which CLAUDE.md file should be updated (root or a specific directory's)
> - The section it belongs in (existing section name, or suggest a new one)
> - The proposed addition (1-3 lines, written in the style of the existing CLAUDE.md)
> - Why this is worth documenting (what would go wrong without it?)
>
> If the PR is routine and doesn't reveal anything new, say so. Don't force suggestions.

## Step 3: Collect and Deduplicate

Wait for all agents to complete. Merge results:
- Deduplicate issues that multiple agents flagged
- Group by file

## Step 4: Present Results

Format the output:

```
## PR Review — #<number>: <title>

### Bugs (N)
| File | Lines | Severity | Description |
|------|-------|----------|-------------|

### CLAUDE.md Violations (N)
| File | Lines | Rule | Violation |
|------|-------|------|-----------|

### Suggested CLAUDE.md Updates (N)
For each suggestion:
> **Add to `<path>/CLAUDE.md`** (section: <section>)
> `<proposed text>`
> *Why:* <rationale>

### Summary
- X bugs, Y compliance issues, Z CLAUDE.md update suggestions
- [If no issues at all]: "Clean PR. No bugs, no compliance issues, no CLAUDE.md gaps."
```

## Step 5: Post Comments (if `--comment`)

If the user passed `--comment`:

1. For bugs and compliance issues: post inline comments on the PR via `gh pr comment` or
   the GitHub inline comment MCP tool if available.
2. For CLAUDE.md update suggestions: post a single summary comment (not inline) with all
   suggestions grouped together, prefixed with:
   > **CLAUDE.md update suggestions** — This PR introduces patterns not yet documented.
   > Consider adding these before merging:
3. If no issues found, post:
   > ## Code review
   > No issues found. Checked for bugs, CLAUDE.md compliance, and documentation gaps.

## Step 6: Offer to Apply CLAUDE.md Updates

After presenting results, if there are CLAUDE.md update suggestions, ask:

> Want me to apply these CLAUDE.md updates? (all / pick numbers / skip)

If the user agrees, edit the CLAUDE.md files and create a commit on the PR branch.

## False Positive Filters

Do NOT flag any of these (applies to all agents):
- Pre-existing issues not introduced by this PR
- Code that looks wrong but is actually correct in context
- Style preferences or subjective suggestions
- Issues a linter or formatter would catch
- Lint/type-check suppressions that are explicitly silenced in code
- Generic advice ("consider adding tests") unless CLAUDE.md explicitly requires it
