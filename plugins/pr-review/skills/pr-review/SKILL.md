---
name: pr-review
description: "Use this skill when the user asks to review a PR, check a pull request, or mentions
  /pr-review. Runs specialized review agents for bugs, tests, error handling, comments, types,
  simplification, and CLAUDE.md documentation gaps."
---

Comprehensive PR review with 7 specialized agents. Each focuses on a different angle — bugs,
test coverage, error handling, comment accuracy, type design, code simplification, and CLAUDE.md
documentation gaps.

## Arguments

- `$ARGUMENTS`:
  - A PR number, URL, or branch name — review that PR
  - `--comment` — post findings as GitHub PR comments
  - Review aspects (space-separated): `bugs`, `tests`, `errors`, `comments`, `types`, `simplify`, `docs`
  - `all` — run all applicable agents (default)
  - *(empty)* — detect the current branch's open PR, run all applicable agents

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
   Read each one. If none exist, note this — Agent 7 will suggest creating one.
6. **Classify changed files** to determine which agents run:
   - Any code changed → **always**: Bug Scanner, Code Reviewer/Simplifier, CLAUDE.md Gaps
   - Test files changed or new functionality added → **add**: Test Coverage Analyzer
   - Error handling code changed (try/catch, Result types, fallbacks) → **add**: Silent Failure Hunter
   - Comments or docstrings added/modified → **add**: Comment Analyzer
   - New types/interfaces/classes introduced → **add**: Type Design Analyzer

## Step 2: Launch Review Agents

Spawn applicable agents in parallel (Tier 1/2) or run sequentially (Tier 3). Give every agent
the PR title, description, diff, and any relevant CLAUDE.md content.

---

### Agent 1: Bug Scanner

**Runs:** Always | **Model:** opus if available, sonnet otherwise

> Review this PR diff for bugs. Focus ONLY on changed code. Flag issues where:
> - Code will fail to compile or parse (syntax errors, missing imports, type errors)
> - Code will definitely produce wrong results (clear logic errors)
> - Security vulnerabilities in the changed code (injection, auth bypass, data exposure)
>
> Rate each issue 0-100 confidence. **Only report issues at 80+.**
>
> Do NOT flag: style issues, potential issues dependent on specific inputs, nitpicks, or
> anything a linter would catch. If you're not certain, don't flag it.
>
> For each issue: file, line range, confidence score, description, suggested fix.

---

### Agent 2: Test Coverage Analyzer

**Runs:** When test files change or new functionality is added | **Model:** sonnet

> Analyze test coverage quality for this PR. Focus on behavioral coverage, not line counts.
>
> Look for:
> - Critical code paths with no test coverage
> - Missing edge case and boundary condition tests
> - Missing negative/error case tests
> - Tests that are brittle (testing implementation instead of behavior)
>
> Rate each gap 1-10 (10 = will cause production issues if untested).
> **Only report gaps rated 7+.**
>
> For each gap: what's untested, what could break, a concrete test description.

---

### Agent 3: Silent Failure Hunter

**Runs:** When error handling code changes | **Model:** sonnet

> Hunt for silent failures and inadequate error handling in this PR.
>
> Look for:
> - Empty or overly broad catch blocks that could hide unrelated errors
> - Errors caught but not logged or surfaced to users
> - Fallback behavior that masks real problems without user awareness
> - Missing error handling on operations that can fail (I/O, network, parsing)
> - Catch blocks where you can list specific unexpected errors that would be hidden
>
> Rate each issue: CRITICAL (silent failure, broad catch hiding errors), HIGH (poor error
> message, unjustified fallback), MEDIUM (missing context in logs).
> **Only report CRITICAL and HIGH.**
>
> For each issue: file, lines, severity, what errors could be hidden, suggested fix.

---

### Agent 4: Comment Analyzer

**Runs:** When comments or docstrings are added/modified | **Model:** sonnet

> Analyze code comments in this PR for accuracy and long-term value.
>
> Check:
> - **Factual accuracy**: Do comments match what the code actually does? Do documented
>   parameters, return types, and edge cases match the implementation?
> - **Comment rot risk**: Will these comments become misleading as the code evolves?
> - **Value**: Do comments explain "why" (valuable) or just restate "what" (remove)?
> - **Misleading elements**: Ambiguous language, outdated references, stale TODOs
>
> Only flag comments that are **factually wrong**, **actively misleading**, or **should be
> removed** because they add no value. Don't flag missing comments — that's not this agent's job.
>
> For each issue: file, line, what's wrong, suggested rewrite or "remove".

---

### Agent 5: Type Design Analyzer

**Runs:** When new types, interfaces, or classes are introduced | **Model:** sonnet

> Analyze new types introduced in this PR for design quality.
>
> For each new type, evaluate:
> - **Encapsulation** (1-10): Are internals properly hidden? Can invariants be violated externally?
> - **Invariant expression** (1-10): Are constraints obvious from the type definition?
> - **Invariant enforcement** (1-10): Are invariants checked at construction? All mutation guarded?
>
> Flag:
> - Types that expose mutable internals
> - Missing validation at construction boundaries
> - Invariants enforced only through documentation, not code
> - Anemic types with no behavior (just data bags when they should enforce rules)
>
> **Only report types scoring below 6 on any dimension.**
> Be pragmatic — a simple DTO doesn't need the same rigor as a domain model.
>
> For each type: name, ratings, specific concerns, concrete improvement suggestions.

---

### Agent 6: Code Simplifier

**Runs:** Always (last — after other agents finish) | **Model:** opus if available, sonnet otherwise

> Review the changed code for unnecessary complexity.
>
> Look for:
> - Overly nested logic that could be flattened (early returns, guard clauses)
> - Redundant code or abstractions that add no value
> - Overly clever solutions that are hard to understand
> - Nested ternaries that should be if/else or switch
> - Code that could be simpler without losing clarity or functionality
>
> **Do not suggest changes that trade readability for brevity.** Three clear lines beat one
> dense one-liner. Only suggest simplifications where the result is genuinely easier to
> understand.
>
> For each suggestion: file, lines, current pattern, simpler alternative, why it's better.

---

### Agent 7: CLAUDE.md Gap Detector

**Runs:** Always | **Model:** haiku

> Review this PR to see if it reveals patterns worth documenting in CLAUDE.md.
>
> Look for:
> - New conventions this PR establishes (naming, file organization, API patterns)
> - Non-obvious decisions (why something was done a certain way)
> - Gotchas the author hit (workarounds, edge cases, things that broke)
> - New dependencies or tooling that affect how others write code
>
> Cross-reference existing CLAUDE.md files. Only suggest things NOT already documented.
>
> If CLAUDE.md doesn't exist yet, suggest creating one with the top 3 patterns from this PR.
> If the PR is routine, say "No documentation gaps" and stop. Don't force suggestions.
>
> For each suggestion: which CLAUDE.md, proposed text (1-2 lines), why it matters.

---

## Step 3: Collect and Filter

Wait for all agents. Then:

1. **Deduplicate** issues flagged by multiple agents
2. **Filter false positives** — remove:
   - Pre-existing issues not introduced by this PR
   - Issues explicitly silenced in code (lint-ignore, type suppressions)
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
- **[Error Handling]** `api.ts:78` — Silent catch hides TypeError
  *Fix:* suggested fix
- **[Test Gap]** Missing test for X (criticality: 8/10)
  *Test:* concrete test description
- **[Type Design]** `UserState` — encapsulation 4/10, mutable internals exposed
  *Fix:* suggested improvement

### Suggestions (N)
- **[Simplify]** `utils.ts:30-45` — Nested ternary → early return
- **[Comment]** `auth.ts:12` — Docstring says "returns null" but returns undefined

### CLAUDE.md Updates (N)
> **Add to `CLAUDE.md`** (section: Error Handling)
> `Always use AppError class for API errors — raw Error() loses stack context`
> *Why:* This PR fixed a debugging issue caused by this.

---
Summary: X critical, Y important, Z suggestions, W CLAUDE.md updates
```

If no issues:
> Clean PR. No bugs, test gaps, or error handling issues found.

## Step 5: Post Comments (if `--comment`)

If `--comment` was passed:
- **Critical and important issues**: Post inline comments on the PR
- **Suggestions**: Post as a single summary comment
- **CLAUDE.md updates**: Post as a separate summary comment, prefixed:
  > **CLAUDE.md update suggestions** — consider adding these before merging:
- **No issues**: Post "No issues found" summary

## Step 6: Offer to Apply

After presenting results:
- If there are **code simplifications** the user approves, apply them
- If there are **CLAUDE.md suggestions**, ask:
  > Want me to apply these CLAUDE.md updates? (all / pick numbers / skip)
- If agreed, edit the files and commit to the PR branch

## False Positive Filters

These apply across ALL agents — do NOT flag:
- Pre-existing issues not introduced by this PR
- Code that looks wrong but is correct in context
- Issues explicitly silenced (lint-ignore comments, type suppressions)
- Style preferences or subjective opinions
- Anything a linter or formatter would catch
- Generic advice unless CLAUDE.md specifically requires it

**High signal only.** Every flagged issue should be worth the reviewer's time.
