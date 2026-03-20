---
name: spawn-team
description: "Use this skill whenever the user asks to spin up a team of agents, use split panes, run agents in parallel with coordination, or mentions 'swarm'. Also use proactively when a task would clearly benefit from multiple coordinated agents working in split panes."
---

Spin up a coordinated team of agents that appear in split panes in the terminal UI.

## CRITICAL: Team agents require TeamCreate

Plain `Agent` tool calls do NOT create split panes — they run as background subagents. To get split panes, you MUST:

1. **Create a team first** with `TeamCreate`
2. **Spawn agents with `team_name`** parameter set to the team name

## Arguments
- `$ARGUMENTS` (optional):
  - *(empty)* — ask the user what agents they need
  - Agent descriptions — parse and create the requested agents

## Workflow

### Step 1: Create the Team

Use `TeamCreate` with a descriptive team name:
```
TeamCreate:
  team_name: "<descriptive-kebab-case-name>"
  description: "<what the team is working on>"
```

### Step 2: Spawn Agents

Use the `Agent` tool for each agent, always including:
- `team_name`: must match the team name from Step 1
- `name`: a short kebab-case name for the agent (used for messaging)
- `prompt`: clear instructions for what the agent should do

Spawn all agents in parallel (multiple Agent tool calls in one message) for them to appear as split panes simultaneously.

```
Agent:
  name: "agent-name"
  team_name: "<team-name>"
  prompt: "<task instructions>"
```

### Step 3: Coordinate

- Agents communicate via `SendMessage` (type: "message" for DMs, "broadcast" for all)
- Track work with `TaskCreate` / `TaskUpdate` if needed
- Agents go idle between turns — this is normal. Send them a message to wake them up.

### Step 4: Cleanup

When work is done:
1. Send `shutdown_request` to each agent via `SendMessage`
2. Wait for shutdown confirmations
3. Call `TeamDelete` to clean up team and task directories

## Common Mistakes to Avoid

- **DO NOT** use plain `Agent` calls without `team_name` — no split panes will appear
- **DO NOT** forget `TeamCreate` before spawning agents
- **DO NOT** use `run_in_background: true` with team agents — they manage their own lifecycle
- **DO** spawn all agents in a single message for parallel split pane creation
- **DO** use `SendMessage` for all inter-agent communication (plain text output is not visible to teammates)
