---
name: hazel-snowflake-query
description: "Use this skill when the user asks to query Snowflake, analyze Hazel Health data,
  run SQL, or mentions tables like MART_VISIT, DIM_PATIENT, TETRIS_RANKED_SCHEDULING, or any
  HAZEL_EDW/HAZEL_STREAM schema. Also triggers on /snowflake or /query."
---

Query harness for Hazel Health's Snowflake data warehouse. Ensures Claude queries Snowflake
correctly via the CLI, loads the semantic layer for accurate SQL, and falls back gracefully when
setup is incomplete.

## 1. Prerequisites Check

Before querying, verify the Snowflake CLI is available:

1. Run `snow --version` via Bash to confirm the CLI is installed.
2. Run `snow connection test` via Bash to verify the default connection works.
3. If both succeed, proceed to **Section 2**.
4. If `snow` is not found or the connection test fails, read the bundled fallback:

```
Read: {SKILL_DIR}/reference/setup-fallback.md
```

Present the setup instructions to the user and stop. Do not attempt to query without a working CLI connection.

## 2. Semantic Layer Detection

The semantic layer contains table definitions, column descriptions, enums, and SQL patterns that
make queries accurate. Search for it in priority order — stop at the first hit.

**Validation:** Any match must contain the text "Semantic Layer Quick Reference" in its first 10
lines. If not, skip it and continue searching.

### Step 1: Current working directory and parents

```
Glob: **/00-semantic-layer/_index.md   (in CWD)
Glob: **/semantic-layer/_index.md      (in CWD)
```

### Step 2: Common local folders

Search common locations where users keep Claude Code projects or data files. Run all globs in
parallel — stop at the first validated hit.

**Documents/Claude variants:**
```
~/Documents/[Cc]laude*/**/semantic-layer/_index.md
~/Documents/[Cc]laude*/**/00-semantic-layer/_index.md
~/Documents/data-projects/**/semantic-layer/_index.md
~/Documents/data-projects/**/00-semantic-layer/_index.md
```

**Desktop and home root:**
```
~/Desktop/[Cc]laude*/**/semantic-layer/_index.md
~/Desktop/[Cc]laude*/**/00-semantic-layer/_index.md
~/[Cc]laude*/**/semantic-layer/_index.md
~/[Cc]laude*/**/00-semantic-layer/_index.md
```

### Step 3: Google Drive for Desktop

If the user has Google Drive for Desktop, the "Snowflake Semantic Layer" shared drive syncs
locally. The wildcard `*` handles any Google account email.

```
~/Library/CloudStorage/GoogleDrive-*/**/Snowflake Semantic Layer/**/semantic-layer/_index.md
~/Library/CloudStorage/GoogleDrive-*/**/Snowflake Semantic Layer/**/00-semantic-layer/_index.md
~/Library/CloudStorage/GoogleDrive-*/**/semantic-layer/_index.md
```

### Step 4: Not found — fallback

If no semantic layer is found after all steps:

1. Read the bundled fallback: `{SKILL_DIR}/reference/setup-fallback.md`
2. Present setup options to the user:
   - Download from [Google Drive](https://drive.google.com/drive/u/0/folders/0ALLHSZxpentJUk9PVA)
   - Follow the Claude Code Setup Guide Steps 8-9
3. You **can still query** without the semantic layer, but warn the user that column names and
   filter values may be inaccurate. Offer to run `DESCRIBE TABLE` commands to discover schema.

### Once found

When the semantic layer `_index.md` is located:

1. **Read `_index.md`** — gives table overview, key joins, gotchas, and domain file index
2. **Read `ai-prompt.md`** (same directory) — concise rules for accurate SQL (<2K tokens)
3. Store the semantic layer base path for subsequent domain file lookups

## 3. Query Workflow

Follow this procedure for every query:

1. **Understand the question.** Identify which tables and metrics are needed. Use the Table
   Disambiguation section in `_index.md` if multiple tables seem relevant.

2. **Check domain files.** Read the relevant `-core.md` domain file for column definitions.
   Only read `-extended.md` if the core file doesn't cover the needed columns.

3. **Check enums.** Before using filter values (e.g., `visit_state`, `product_type`,
   `referral_type`), read `reference/enums.md` for valid values. Incorrect filter values are
   the #1 cause of wrong results.

4. **Write SQL.** Follow the SQL style in `patterns/sql-style.md`. Use fully qualified schema
   names (e.g., `HAZEL_EDW.MART.MART_VISIT`).

5. **Run the query.** Use `snow sql -q "YOUR SQL"` via Bash (uses the `default` connection).
   For multi-line SQL, write the query to a temp file and use `snow sql -f /tmp/query.sql`.

6. **Validate results.** Cross-check row counts and values against `reference/sanity-checks.md`
   expected ranges. If results look wrong, check gotchas before re-running.

7. **Present results.** Format as markdown tables. Include the SQL used so the user can verify.

## 4. Reference Table

| Need | File to read |
|------|-------------|
| Table overview, key joins | `_index.md` |
| AI rules, quick start | `ai-prompt.md` |
| Visit columns | `domains/visits-core.md` |
| RCM / billing columns | `domains/rcm-core.md` |
| Referral columns | `domains/referrals-core.md` |
| Provider columns | `domains/providers-core.md` |
| Patient columns | `domains/patients-core.md` |
| School / district columns | `domains/schools.md` |
| Valid filter values (enums) | `reference/enums.md` |
| Metric definitions + SQL | `reference/metrics.md` |
| Population defaults | `reference/defaults.md` |
| Business funnels | `reference/funnels.md` |
| Common join patterns | `patterns/common-joins.md` |
| SQL style conventions | `patterns/sql-style.md` |
| Known gotchas (50+) | `patterns/gotchas.md` |
| Validation queries | `reference/golden-queries.md` |
| Result sanity checks | `reference/sanity-checks.md` |

## 5. Error Handling

| Error | Action |
|-------|--------|
| Column not found | Run `DESCRIBE TABLE schema.table` to discover actual column names |
| Connection failed | Read `{SKILL_DIR}/reference/setup-fallback.md` and present setup steps |
| Wrong results | Check `patterns/gotchas.md` — especially enum casing, join fan-out, and schema paths |
| Table not found | Verify schema path (DIM tables are in `HAZEL_EDW.CORE`, not `MART`) |
| Permission denied | User may need CLAUDE_READ_ONLY_ROLE — check `~/.snowflake/config.toml` |
| `snow` command not found | Install the Snowflake CLI — see `{SKILL_DIR}/reference/setup-fallback.md` |
