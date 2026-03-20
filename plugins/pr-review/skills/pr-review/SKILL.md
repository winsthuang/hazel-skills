---
name: pr-review
description: "Use this skill when the user asks to review a PR, check a pull request, or mentions
  /pr-review. Runs specialized review agents for bugs, test coverage, error handling, and
  CLAUDE.md documentation gaps."
---

Comprehensive PR review that catches bugs, test gaps, error handling issues, and — for teams
adopting CLAUDE.md — surfaces patterns worth documenting. Combines high-signal-only bug detection
with practical specialized agents.

## Arguments

- `$ARGUMENTS`:
  - A PR number, URL, or branch name — review that PR
  - `--comment` — post findings as GitHub PR comments
  - Review aspects (space-separated): `bugs`, `tests`, `errors`, `simplify`, `docs`
  - `all` — run all agents (default)
  - *(empty)* — detect the current branch's open PR, run all agents

## Execution Model

Adapt to available capabilities — try each tier in order, use the first that works.

**Tier 1 — Team agents (split panes):** If `TeamCreate` is available, create a team and spawn
agents with `team_name`. Agents appear in split panes.

**Tier 2 — Parallel subagents:** If `TeamCreate` is unavailable but `Agent` tool works, spawn
agents in parallel as background subagents.

**Tier 3 — Sequential:** Run all review steps one at a time in the current context. Slower but
works everywhere.

---

## Step 1: Gather Context

1. **Identify the PR.** Use argument if given, otherwise detect via `gh pr view`.
2. **Skip if not reviewable.** Stop if the PR is closed, a draft, or trivially automated (e.g.,
   dependency bumps with no logic changes). Say why and stop.
3. **Fetch the diff:** `gh pr diff <PR>`
4. **Fetch metadata:** `gh pr view <PR> --json title,body,files,headRefName`
5. **Find CLAUDE.md files:** Root `CLAUDE.md` plus any in directories containing changed files.
   Read each one. If none exist, note this — Agent 4 will suggest creating one.
6. **Classify changed files** to determine which agents apply:
   - Test files changed → include test analyzer
   - Error handling code changed (try/catch, Result types, error callbacks) → include error hunter
   - Any code changed → always include bug scanner and code reviewer

## Step 2: Launch Review Agents

Spawn applicable agents in parallel (Tier 1/2) or run sequentially (Tier 3). Give every agent
the PR title, description, and diff.

### Agent 1: Bug Scanner

**Model preference:** opus if available, sonnet otherwise

> Review this PR diff for bugs. Focus ONLY on changed code. Flag issues where:
> - Code will fail to compile or parse (syntax errors, missing imports, type errors)
> - Code will definitely produce wrong results (clear logic errors)
> - Security vulnerabilities in the changed code (injection, auth bypass, data exposure)
>
> Rate each issue 0-100 confidence. Only report issues at 80+.
>
> Do NOT flag: style issues, potential issues dependent on specific inputs, nitpicks, or
> anything a linter would catch. If you're not certain, don't flag it.
>
> For each issue: file, line range, confidence score, description, suggested fix.

### Agent 2: Test Coverage Analyzer

**Only if test files are changed or new functionality is added.**

**Model preference:** sonnet

> Analyze test coverage quality for this PR. Focus on behavioral coverage, not line counts.
>
> Look for:
> - Critical code paths with no test coverage
> - Missing edge case and boundary condition tests
> - Missing negative/error case tests
> - Tests that are brittle (testing implementation instead of behavior)
>
> Rate each gap 1-10 (10 = will cause production issues if untested).
> Only report gaps rated 7+.
>
> For each gap: what's untested, what could break, a concrete test description.

### Agent 3: Error Handling Review

**Only if error handling code is changed (try/catch, error callbacks, fallback logic).**

**Model preference:** sonnet

> Hunt for silent failures and inadequate error handling in this PR.
>
> Look for:
> - Empty or overly broad catch blocks that could hide errors
> - Errors that are caught but not logged or surfaced to users
> - Fallback behavior that masks real problems
> - Missing error handling on operations that can fail (I/O, network, parsing)
>
> Rate each issue: CRITICAL (silent failure), HIGH (poor error message), MEDIUM (missing context).
> Only report CRITICAL and HIGH.
>
> For each issue: file, lines, severity, what errors could be hidden, suggested fix.

### Agent 4: CLAUDE.md Gap Detector

**Always runs. Lightweight — this agent reads the diff and existing CLAUDE.md, nothing more.**

**Model preference:** haiku (fast, cheap — this is a suggestion agent, not a gatekeeper)

> Review this PR to see if it reveals patterns worth documenting in CLAUDE.md.
>
> Look for:
> - New conventions this PR establishes (naming, file organization, API patterns)
> - Non-obvious decisions (why something was done a certain way, visible in code comments or PR description)
> - Gotchas the author hit (workarounds, edge cases, things that broke)
> - New dependencies or tooling that affect how others write code
>
> Cross-reference existing CLAUDE.md files. Only suggest things NOT already documented.
>
> If CLAUDE.md doesn't exist yet, suggest creating one with the top 3 patterns from this PR.
>
> If the PR is routine, say "No documentation gaps" and stop. Don't force suggestions.
>
> For each suggestion: which CLAUDE.md, proposed text (1-2 lines), why it matters.

## Step 3: Collect and Filter

Wait for all agents. Then:

1. **Deduplicate** issues flagged by multiple agents
2. **Filter false positives** — remove:
   - Pre-existing issues not introduced by this PR
   - Issues explicitly silenced in code (lint-ignore comments, type suppressions)
   - Nitpicks a senior engineer wouldn't flag
   - Generic advice ("add more tests") unless CLAUDE.md specifically requires it
3. **Group by severity**: Critical → Important → Suggestions → CLAUDE.md updates

## Step 4: Present Results

```
## PR Review — #<number>: <title>

### Critical Issues (N)
- **[Bug]** `file.ts:42` — Description (confidence: 95)
  *Fix:* suggested fix

### Important Issues (N)
- **[Error Handling]** `api.ts:78` — Description
  *Fix:* suggested fix
- **[Test Gap]** Missing test for X (criticality: 8/10)
  *Test:* concrete test description

### CLAUDE.md Updates (N)
> **Suggestion:** Add to `CLAUDE.md` (section: Error Handling)
> `Always use AppError class for API errors — raw Error() loses stack context`
> *Why:* This PR fixed a debugging issue caused by this; worth preventing for others.

---
Summary: X critical, Y important, Z CLAUDE.md suggestions
```

If no issues found:
> Clean PR. No bugs, test gaps, or error handling issues found. Checked N files across M agents.

## Step 5: Post Comments (if `--comment`)

If `--comment` was passed:
- **Bugs and error handling issues**: Post inline comments on the PR
- **Test gaps**: Post as a single summary comment
- **CLAUDE.md suggestions**: Post as a separate summary comment, prefixed:
  > **CLAUDE.md update suggestions** — consider adding these before merging:
- **No issues**: Post "No issues found" summary

## Step 6: Offer to Apply

If there are CLAUDE.md suggestions, ask:
> Want me to apply these CLAUDE.md updates? (all / pick numbers / skip)

If agreed, edit the files and commit to the PR branch.

## Notes

- **High signal only.** Every flagged issue should be worth the reviewer's time. One false
  positive costs more trust than ten missed nitpicks.
- **CLAUDE.md suggestions are gentle.** They're in a separate section, lowest priority, and
  framed as suggestions. The goal is to build the habit, not block the PR.
- **Agents are independent.** Each gets the same diff and context but reviews from a different
  angle. This avoids blind spots without redundant work.
