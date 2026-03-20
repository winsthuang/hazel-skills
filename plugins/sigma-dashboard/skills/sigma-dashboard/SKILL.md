---
name: sigma-dashboard
description: "Use this skill when the user asks about Sigma Computing dashboards, wants to extract
  SQL from Sigma workbooks, list Sigma dashboards, or inspect what tables/columns a Sigma dashboard
  uses. Also triggers on /sigma."
---

Interact with Sigma Computing dashboards via the Sigma REST API v2. Extracts compiled SQL from
workbook elements and lists workbooks.

## 1. Prerequisites Check

The Sigma integration lives in a project directory. Locate it:

### Step 1: Search

Glob for the Sigma client:

```
Glob: **/sigma-integration/sigma_client.py
```

Try these roots in order:
- Current working directory
- `~/Documents/`
- `~/Desktop/`

If found, set `SIGMA_DIR` to the parent directory.

### Step 2: Verify environment

1. Check that `.env` exists in `SIGMA_DIR` (contains API credentials).
2. Check that `SIGMA_DIR/.venv` exists OR that `httpx` and `sqlglot` are importable.

If `.env` is missing:
- Show the user the `.env.example` template from `SIGMA_DIR/.env.example`
- Tell them to get API credentials from a Sigma admin:
  **Sigma > Administration > Developer Access > Create new API client**
- Base URL for Hazel is `https://aws-api.sigmacomputing.com` (AWS US region)
- Stop and wait for the user to set up credentials.

If dependencies are missing, run:
```bash
cd SIGMA_DIR && python3 -m pip install httpx python-dotenv sqlglot
```

## 2. Available Operations

### List workbooks

```bash
cd SIGMA_DIR && python3 extract_queries.py --list-only
```

Shows all workbooks the API client can access, with tags.

To list only Production-tagged workbooks:
```bash
cd SIGMA_DIR && python3 extract_queries.py --list-only --production-only
```

### Extract SQL from workbooks

Extract all workbooks:
```bash
cd SIGMA_DIR && python3 extract_queries.py
```

Extract a specific workbook by name (case-insensitive substring match):
```bash
cd SIGMA_DIR && python3 extract_queries.py --workbook-name "State of the Business"
```

Extract by workbook ID:
```bash
cd SIGMA_DIR && python3 extract_queries.py --workbook-id <id>
```

Extract only Production-tagged workbooks:
```bash
cd SIGMA_DIR && python3 extract_queries.py --production-only
```

Output goes to `SIGMA_DIR/output/<workbook-name>/` with:
- One `.sql` file per element (organized by page)
- A `manifest.json` with element metadata

### Inspect a specific dashboard's SQL

After extraction, read the SQL files directly:
```bash
ls SIGMA_DIR/output/<workbook-name>/
```

Then read individual `.sql` files to see the compiled Snowflake SQL for each element.

## 3. Using the API Client Directly

For custom queries not covered by the CLI scripts, use `sigma_client.py` in a Python session:

```python
import sys
sys.path.insert(0, "SIGMA_DIR")
from sigma_client import SigmaClient

with SigmaClient() as client:
    # List all workbooks
    workbooks = client.list_workbooks()

    # Get a specific workbook
    wb = client.get_workbook("workbook-id")

    # List pages in a workbook
    pages = client.list_pages("workbook-id")

    # List elements on a page
    elements = client.list_elements("workbook-id", "page-id")

    # Get compiled SQL for an element
    query = client.get_element_query("workbook-id", "element-id")
    print(query["sql"])

    # Get column metadata for an element
    columns = client.get_element_columns("workbook-id", "element-id")

    # List all members
    members = client.list_members()

    # List all tags
    tags = client.list_tags()
```

## 4. Key Details

- **Auth**: Client credentials grant (client_id + client_secret, base64-encoded). Tokens auto-refresh.
- **Region**: Hazel uses AWS US (`https://aws-api.sigmacomputing.com`)
- **Pagination**: All list endpoints auto-paginate (100 items per page).
- **Rate limits**: Sigma API has rate limits; the client does not retry automatically.
- **Output directory**: `SIGMA_DIR/output/` — gitignored, safe to delete and re-extract.

## 5. Troubleshooting

| Error | Fix |
|-------|-----|
| `SIGMA_CLIENT_ID` not set | Create `.env` from `.env.example` with valid credentials |
| 401 Unauthorized | Credentials may be revoked — get new ones from Sigma admin |
| 403 Forbidden | API client may lack permissions — ask admin to check scope |
| Workbook not found | Use `--list-only` to verify the workbook name/ID |
| Empty SQL for elements | Text, image, and container elements have no SQL — this is expected |
