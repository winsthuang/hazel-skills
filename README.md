# Claude Code Skills

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for Hazel Health workflows.

Modeled after [`anthropics/skills`](https://github.com/anthropics/skills).

## Included Skills

| Skill | Description |
|-------|-------------|
| [`hazel-snowflake-query`](skills/hazel-snowflake-query/) | Query harness for Hazel Health's Snowflake data warehouse with automatic semantic layer detection |

## Installation

Copy the skill folder into your Claude Code skills directory:

```bash
# Clone the repo
git clone https://github.com/winstonhuang/claude-code-skills.git

# Copy the skill you want
cp -r claude-code-skills/skills/hazel-snowflake-query ~/.claude/skills/
```

Or install a single skill directly:

```bash
mkdir -p ~/.claude/skills/hazel-snowflake-query/reference
curl -sL https://raw.githubusercontent.com/winstonhuang/claude-code-skills/main/skills/hazel-snowflake-query/SKILL.md \
  -o ~/.claude/skills/hazel-snowflake-query/SKILL.md
curl -sL https://raw.githubusercontent.com/winstonhuang/claude-code-skills/main/skills/hazel-snowflake-query/reference/setup-fallback.md \
  -o ~/.claude/skills/hazel-snowflake-query/reference/setup-fallback.md
```

## Prerequisites

The `hazel-snowflake-query` skill requires:

1. **Snowflake MCP server** configured in `.mcp.json` — see [setup instructions](skills/hazel-snowflake-query/reference/setup-fallback.md)
2. **Semantic layer** (optional but recommended) — download from the [Snowflake Semantic Layer](https://drive.google.com/drive/u/0/folders/0ALLHSZxpentJUk9PVA) shared drive

## Usage

Once installed, the skill activates automatically when you:

- Ask Claude to query Snowflake or analyze Hazel Health data
- Mention tables like `MART_VISIT`, `DIM_PATIENT`, or `TETRIS_RANKED_SCHEDULING`
- Use `/snowflake` or `/query`

## License

Apache 2.0 — see [LICENSE](LICENSE).
