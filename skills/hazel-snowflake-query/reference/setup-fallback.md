# Snowflake MCP Setup for Claude Code

You need two things to query Snowflake from Claude Code: the **MCP server** (connection) and the
**semantic layer** (data dictionary). Follow the steps below.

## MCP Server Setup (~10 min)

### 1. Install uv

```bash
brew install uv
```

### 2. Get the private key

Ask Winston for the `claude_mcp_key.p8` file, then:

```bash
mkdir -p ~/.snowflake/keys
# Copy the key file to ~/.snowflake/keys/claude_mcp_key.p8
chmod 600 ~/.snowflake/keys/claude_mcp_key.p8
```

### 3. Configure the Snowflake connection

Create or edit `~/.snowflake/config.toml`:

```toml
[connections.claude_mcp]
account = "HAZELHEALTHORG-HAZELHEALTH"
user = "CLAUDE_CODE_READER"
role = "CLAUDE_READ_ONLY_ROLE"
warehouse = "COMPUTE_WH"
authenticator = "SNOWFLAKE_JWT"
private_key_path = "~/.snowflake/keys/claude_mcp_key.p8"
```

### 4. Add the MCP config

Add to your project's `.mcp.json` (or `~/.claude/.mcp.json` for global access):

```json
{
  "mcpServers": {
    "snowflake": {
      "command": "uvx",
      "args": [
        "snowflake-labs-mcp",
        "--connection-name", "claude_mcp"
      ]
    }
  }
}
```

### 5. Verify

Restart Claude Code, then ask: "List the tables in HAZEL_EDW.MART"

---

## Semantic Layer Setup

The semantic layer gives Claude context about table structure, column definitions, and business
terms. Without it, queries may use wrong column names or filter values.

### Option A: Download from Google Drive

1. Open the [Snowflake Semantic Layer](https://drive.google.com/drive/u/0/folders/0ALLHSZxpentJUk9PVA) shared drive
2. Download the `semantic-layer` folder
3. Move it into your Claude working directory:

```bash
mv ~/Downloads/semantic-layer ~/Documents/Claude/semantic-layer
```

### Option B: Google Drive offline sync (auto-updating)

If you have Google Drive for desktop, the files sync to:

```
~/Library/CloudStorage/GoogleDrive-yourname@hazel.co/
  Shared drives/Snowflake Semantic Layer/semantic-layer/
```

The skill will detect this location automatically.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Connection error | Check private key path in `~/.snowflake/config.toml` |
| Permission denied | Verify key file has `chmod 600` permissions |
| `uvx` not found | Run `brew install uv` |
| MCP tools not loading | Restart Claude Code after adding `.mcp.json` |
| Wrong query results | Make sure the semantic layer is accessible (see above) |
