# Snowflake CLI Setup for Claude Code

You need two things to query Snowflake from Claude Code: the **Snowflake CLI** (connection) and the
**semantic layer** (data dictionary). Follow the steps below.

## CLI Setup (~5 min)

### 1. Install the Snowflake CLI

```bash
brew tap snowflakedb/snowflake-cli && brew install snowflake-cli
```

### 2. Configure the Snowflake connection

Create or edit `~/.snowflake/config.toml` (replace `YOUR_EMAIL` with your Hazel email):

```toml
[connections.claude_mcp]
account = "HAZELHEALTHORG-HAZELHEALTH"
user = "YOUR_EMAIL@hazel.co"
role = "CLAUDE_READ_ONLY_ROLE"
warehouse = "COMPUTE_WH"
authenticator = "externalbrowser"
```

### 3. Verify the connection

```bash
snow connection test --connection claude_mcp
```

### 5. Test a query

```bash
snow sql -q "SELECT COUNT(*) FROM HAZEL_EDW.MART.MART_VISIT" --connection claude_mcp
```

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
| `snow` not found | Run `brew tap snowflakedb/snowflake-cli && brew install snowflake-cli` |
| Connection error | Check `user` and `account` in `~/.snowflake/config.toml` |
| Browser doesn't open | Ensure `authenticator = "externalbrowser"` is set in config |
| SSO token expired | Re-run the query — a new browser window will open to re-authenticate |
| Wrong query results | Make sure the semantic layer is accessible (see above) |
