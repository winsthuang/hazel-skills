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
/plugin install sigma-dashboard@hazel-skills
/plugin install hazel-brand-guidelines@hazel-skills
```

## Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| [`spawn-team`](plugins/spawn-team/) | productivity | Spin up coordinated teams of agents in split panes |
| [`de-ai-ify`](plugins/de-ai-ify/) | writing | Strip AI-sounding language from any text |
| [`slack-respond`](plugins/slack-respond/) | communication | Slack inbox triage and response drafting |
| [`sigma-dashboard`](plugins/sigma-dashboard/) | data | Extract SQL from Sigma Computing dashboards and inspect workbook queries |
| [`hazel-brand-guidelines`](plugins/hazel-brand-guidelines/) | design | Hazel Health brand colors, typography, and layout patterns |
| [`pr-review`](plugins/pr-review/) | engineering | PR review with CLAUDE.md enforcement — flags bugs, compliance, and missing CLAUDE.md updates |

## Moved plugins

- **`hazel-snowflake-query`** now lives in the `hazel` marketplace, served from the
  `HippoMD/claude` repo. It was maintained in two places and drifted; `HippoMD/claude`
  is now the single home. Install it from there:

  ```bash
  /plugin marketplace add HippoMD/claude
  /plugin install hazel-snowflake-query@hazel
  ```

## Prerequisites

Some plugins have external dependencies:

- **sigma-dashboard**: Requires Sigma Computing API credentials and the `sigma-integration` project
- **slack-respond**: Requires Slack MCP server connected to Claude Code

## License

Apache 2.0 — see [LICENSE](LICENSE).
