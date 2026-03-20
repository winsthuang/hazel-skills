---
name: slack-respond
description: "Use when the user invokes /slack-respond. Finds Slack messages needing attention (mentions, DMs, group DMs), summarizes them with triage priority, and drafts responses in the user's voice."
disable-model-invocation: true
---

Slack inbox triage and response drafting tool. Pulls recent messages needing Winston's attention, summarizes them for quick scanning, then drafts replies in his voice.

## Arguments

- `$ARGUMENTS` (optional):
  - *(empty)* — last 24 hours (default)
  - `15m`, `30m` — relative time window (any number + `m` for minutes)
  - `2h`, `4h`, `8h` — relative time window (any number + `h` for hours)
  - `today` — since midnight
  - `yesterday` — yesterday's messages

## Step 1: Prerequisites

1. Verify Slack MCP is connected by running a lightweight test call:
   ```
   mcp__slack__slack_search_channels with query: "general", limit: 1
   ```
   If this fails, tell the user:
   > Slack MCP is not connected. Add it with:
   > `claude mcp add slack --transport http --scope user <slack-mcp-url>`
   Then stop.

2. Read the Slack writing style guide into context:
   ```
   Read file: /Users/winstonhuang/Library/Mobile Documents/com~apple~CloudDocs/Documents/Claude Code/Slack/CLAUDE.md
   ```
   If the file is missing, warn the user but continue with these defaults: warm, direct, lowercase in DMs, `!!` for enthusiasm, short fragments, no formal sign-offs.

## Step 2: Compute Time Window

Parse `$ARGUMENTS` into a Unix timestamp using Bash `date` commands (macOS/BSD syntax). Use the `after` parameter (Unix timestamp) on the search tool instead of `after:YYYY-MM-DD` in the query string — this gives true sub-day precision.

| Argument | Bash command |
|---|---|
| `Nm` (e.g. `15m`, `30m`) | `date -v-Nm +%s` |
| `Nh` (e.g. `2h`, `4h`, `8h`) | `date -v-Nh +%s` |
| *(empty)* or `24h` | `date -v-24H +%s` |
| `today` | `date -j -f "%Y-%m-%d" "$(date +%Y-%m-%d)" +%s` (midnight today) |
| `yesterday` | `date -j -f "%Y-%m-%d" "$(date -v-1d +%Y-%m-%d)" +%s` (midnight yesterday) |

Store the computed timestamp as `$UNIX_TS` for use in the `after` parameter on search queries.

Also compute a human-readable label for the time window (e.g. "last 24 hours", "last 15 minutes", "last 2 hours", "today", "yesterday") for use in the summary header.

## Step 3: Run 3 Parallel Searches

Use `mcp__slack__slack_search_public_and_private` for all three searches. Run them **in parallel** since they are independent. Use `sort: "timestamp"` and `sort_dir: "desc"` for all.

1. **Mentions**: `query: "<@U09A00TLNV6>"`, `after: "$UNIX_TS"` — catches @-mentions across all channels
2. **DMs**: `query: "to:me"`, `after: "$UNIX_TS"` — direct messages to Winston
3. **Group DMs**: `query: "to:me"`, `after: "$UNIX_TS"` — group DM messages to Winston

If any search returns 20 results (the limit), paginate by calling again with `page: 2`, etc., until fewer than 20 results are returned.

De-duplicate results across all three searches by `(channel_id, message_ts)` pair — the same message may appear in multiple searches.

## Step 4: Filter & Classify

**Filter out:**
- Messages FROM Winston (user ID `U09A00TLNV6`) — we only want messages TO or mentioning him
- Bot messages that are purely informational (e.g. deploy notifications, automated alerts) unless they contain a question or action request

**Classify each remaining message as one of:**

### Needs Response
A message needs a response if ANY of these are true:
- Contains a question mark (`?`)
- Contains request verbs: "can you", "could you", "would you", "please", "need you to", "help with"
- Is a DM where Winston has NOT replied yet in the thread/conversation
- Is a direct @-mention with action language ("review", "check", "approve", "update", "look at", "thoughts?")

### FYI Only
- Announcements, bot messages, informational shares
- Messages Winston has already replied to
- Channel-wide broadcasts not specifically requesting action from Winston
- Reactions-only or emoji-only messages

## Step 5: Present Summary

Before presenting the summary, use `mcp__slack__slack_read_thread` (or `slack_read_channel` for DMs without threads) to pull full conversation context for every "Needs Response" item. The user needs enough context to decide *what* to say — a 1-line summary is not enough.

Present the inbox summary in this format:

```
## Slack Inbox — [time window label]

### Needs Response (N)

**1. #channel-name — @sender, 2h ago**
> [Full context: what the conversation is about, what was said before, what specifically the sender is asking/needing from Winston, and current status — e.g. whether others have already chimed in or if it's been resolved. 2-5 sentences.]

**2. DM from @person — 45m ago**
> [Full context as above. Include the sender's exact question or request when possible. Note the conversation history — what Winston last said, what they replied, what's still open.]

### FYI Only (N)
**3. #channel-name — @sender, 1h ago**
> [1-2 sentence summary — these don't need as much detail since no response is needed]

---
Which messages would you like to respond to? (numbers, "all", or skip)
```

**Important:** The goal is that Winston can read each summary and immediately dictate response intent ("for 1, say X") without needing to open Slack or ask for more context. Err on the side of too much detail rather than too little. Include:
- What the conversation is about (the topic/project)
- What the sender specifically needs from Winston
- What Winston has already said in the thread (if anything)
- Whether the issue appears resolved or still open
- Any relevant replies from others

If no messages are found at all, say:
> Inbox zero! No messages needing attention in the [time window]. Try a broader window: `/slack-respond 30m`, `/slack-respond 8h`, or `/slack-respond yesterday`

Then stop.

## Step 6: Draft Responses (Interactive)

When the user provides response intent (e.g. "for 1 say yes, for 2 tell them I'll check tomorrow"):

For each message the user wants to respond to:

1. **Get full context**: Use `mcp__slack__slack_read_thread` with the message's `channel_id` and `thread_ts` (or `message_ts` if not in a thread) to read the full conversation context.

2. **Draft the response** applying the Slack style guide from Step 1:
   - Match formality to context (DM = very casual lowercase, channel = casual-professional)
   - Use Winston's signature patterns: `!!`, `--`, fragments, "ofc", "yall", "prob", "lemme"
   - Keep DM responses to 1-2 short messages
   - Channel replies can be slightly longer but still concise
   - NEVER sound like an AI wrote it

3. **Present the draft** to the user:
   ```
   **Reply to #channel / @person:**
   > [drafted message]

   Send as draft? (y/n/edit)
   ```

4. **On approval**: Use `mcp__slack__slack_send_message_draft` with:
   - `channel_id`: the channel/DM where the message was
   - `thread_ts`: the thread timestamp (to reply in-thread)
   - `message`: the drafted text

5. **Draft collision handling**: If `slack_send_message_draft` fails because a draft already exists for that channel:
   - Warn the user: "A draft already exists in this channel. Options: (a) send directly with `slack_send_message`, (b) skip, (c) copy to clipboard"
   - If user chooses direct send, use `mcp__slack__slack_send_message` with explicit user approval
   - For multiple threads in the same channel: draft the first, then present remaining as text for the user to send manually or sequentially after the first draft is sent

6. **Report** the draft link for each successfully created draft.

## Step 7: Wrap Up

After all responses are processed:
- Report total count of drafts created
- Note any skipped items or errors
- If there were FYI items, briefly note them as acknowledged

## Error Handling

| Scenario | Action |
|---|---|
| Slack MCP not connected | Print setup instructions and stop (Step 1) |
| No messages found | "Inbox zero!" + suggest broader time window |
| Draft already exists for channel | Warn + offer direct send or skip (Step 6.5) |
| Style guide not found | Warn + use general voice defaults (Step 1.2) |
| One-draft-per-channel limit | Draft first reply, present rest as text for manual send |
| Search pagination needed | Auto-paginate until fewer than 20 results returned |
| Thread read fails | Show original message snippet, draft based on that context alone |
