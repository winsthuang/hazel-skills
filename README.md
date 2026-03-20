# hazel-skills

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin marketplace for Hazel Health workflows.

## Installation

Install plugins from this marketplace:

```bash
/plugin marketplace add winsthuang/hazel-skills
```

Then install individual plugins:

```bash
/plugin install spawn-team@hazel-skills
/plugin install de-ai-ify@hazel-skills
/plugin install slack-respond@hazel-skills
/plugin install hazel-snowflake-query@hazel-skills
/plugin install sigma-dashboard@hazel-skills
/plugin install hazel-brand-guidelines@hazel-skills
```

## Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| [`spawn-team`](plugins/spawn-team/) | productivity | Spin up coordinated teams of agents in split panes |
| [`de-ai-ify`](plugins/de-ai-ify/) | writing | Strip AI-sounding language from any text |
| [`slack-respond`](plugins/slack-respond/) | communication | Slack inbox triage and response drafting |
| [`hazel-snowflake-query`](plugins/hazel-snowflake-query/) | data | Query harness for Hazel Health's Snowflake data warehouse with semantic layer detection |
| [`sigma-dashboard`](plugins/sigma-dashboard/) | data | Extract SQL and run gap analysis on Sigma Computing dashboards |
| [`hazel-brand-guidelines`](plugins/hazel-brand-guidelines/) | design | Hazel Health brand colors, typography, and layout patterns |

## Prerequisites

Some plugins have external dependencies:

- **hazel-snowflake-query**: Requires [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/index) and optionally the semantic layer — see [setup guide](plugins/hazel-snowflake-query/skills/hazel-snowflake-query/reference/setup-fallback.md)
- **sigma-dashboard**: Requires Sigma Computing API credentials and the `sigma-integration` project
- **slack-respond**: Requires Slack MCP server connected to Claude Code

## License

Apache 2.0 — see [LICENSE](LICENSE).
