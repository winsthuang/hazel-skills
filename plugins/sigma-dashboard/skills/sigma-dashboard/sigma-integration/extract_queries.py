#!/usr/bin/env python3
"""Extract compiled SQL from every element in Sigma Computing workbooks.

Usage:
    # Extract all workbooks the API client can access
    python extract_queries.py

    # Extract only Production-tagged workbooks
    python extract_queries.py --production-only

    # Extract a single workbook by name (substring match, case-insensitive)
    python extract_queries.py --workbook-name "Revenue Dashboard"

    # Extract a single workbook by ID
    python extract_queries.py --workbook-id abc-123-def

    # Custom output directory
    python extract_queries.py --output-dir ./my-sql-output
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from sigma_client import SigmaClient


def _sanitize(name: str) -> str:
    """Turn an arbitrary name into a safe filesystem directory/file name."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.strip(". ")
    return name or "unnamed"


def _get_workbook_tags(client: SigmaClient, workbook_id: str) -> list[str]:
    """Get tag names for a workbook, returning empty list on failure."""
    try:
        tags = client.get_workbook_tags(workbook_id)
        return [t.get("name", "") for t in tags]
    except Exception:
        return []


def extract_workbook(
    client: SigmaClient,
    workbook: dict,
    output_dir: Path,
    tags: list[str] | None = None,
) -> dict:
    """Extract SQL for every element in a workbook. Returns a manifest dict."""
    wb_id = workbook["workbookId"]
    wb_name = workbook.get("name", wb_id)
    wb_dir = output_dir / _sanitize(wb_name)
    wb_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict = {
        "workbookId": wb_id,
        "workbookName": wb_name,
        "tags": tags or [],
        "createdBy": workbook.get("createdBy", ""),
        "updatedAt": workbook.get("updatedAt", ""),
        "elements": [],
    }

    pages = client.list_pages(wb_id)
    print(f"  Workbook '{wb_name}' — {len(pages)} page(s)")

    for page in pages:
        page_id = page["pageId"]
        page_name = page.get("name", page_id)
        page_dir = wb_dir / _sanitize(page_name)
        page_dir.mkdir(parents=True, exist_ok=True)

        elements = client.list_elements(wb_id, page_id)
        print(f"    Page '{page_name}' — {len(elements)} element(s)")

        for elem in elements:
            elem_id = elem["elementId"]
            elem_name = elem.get("name", elem_id)
            elem_type = elem.get("type", "unknown")

            try:
                query_resp = client.get_element_query(wb_id, elem_id)
                sql = query_resp.get("sql", "")
            except Exception as exc:
                print(f"      ⚠ {elem_name} ({elem_type}): could not fetch SQL — {exc}")
                sql = ""

            if not sql:
                print(f"      - {elem_name} ({elem_type}): no SQL (likely a text/image element)")
                continue

            sql_file = page_dir / f"{_sanitize(elem_name)}__{elem_id}.sql"
            sql_file.write_text(sql, encoding="utf-8")
            print(f"      ✓ {elem_name} ({elem_type}) → {sql_file.relative_to(output_dir)}")

            manifest["elements"].append(
                {
                    "elementId": elem_id,
                    "elementName": elem_name,
                    "elementType": elem_type,
                    "pageId": page_id,
                    "pageName": page_name,
                    "sqlFile": str(sql_file.relative_to(wb_dir)),
                }
            )

    manifest_path = wb_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  ✓ Manifest written → {manifest_path.relative_to(output_dir)}")

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract compiled SQL from Sigma Computing workbooks.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--workbook-id", help="Extract only this workbook (by ID)")
    group.add_argument("--workbook-name", help="Extract workbooks matching this name (case-insensitive substring)")
    group.add_argument("--production-only", action="store_true", help="Extract only Production-tagged workbooks")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "output"),
        help="Directory to write SQL files into (default: ./output)",
    )
    parser.add_argument("--list-only", action="store_true", help="List matching workbooks without extracting")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with SigmaClient() as client:
        if args.workbook_id:
            wb = client.get_workbook(args.workbook_id)
            workbooks = [wb]
        else:
            workbooks = client.list_workbooks()
            if args.workbook_name:
                pattern = args.workbook_name.lower()
                workbooks = [w for w in workbooks if pattern in w.get("name", "").lower()]
                if not workbooks:
                    print(f"No workbooks matching '{args.workbook_name}'", file=sys.stderr)
                    sys.exit(1)

        # Fetch tags for each workbook
        wb_tags: dict[str, list[str]] = {}
        if args.production_only or args.list_only:
            print("Fetching tags for workbooks...")
            for wb in workbooks:
                wb_id = wb["workbookId"]
                tags = _get_workbook_tags(client, wb_id)
                wb_tags[wb_id] = tags

        # Filter to Production-tagged workbooks
        if args.production_only:
            workbooks = [
                wb for wb in workbooks
                if "Production" in wb_tags.get(wb["workbookId"], [])
            ]
            if not workbooks:
                print("No Production-tagged workbooks found", file=sys.stderr)
                sys.exit(1)

        print(f"\nFound {len(workbooks)} workbook(s) to process\n")

        if args.list_only:
            for wb in workbooks:
                wb_id = wb["workbookId"]
                tags = wb_tags.get(wb_id, [])
                tag_str = f" [{', '.join(tags)}]" if tags else ""
                print(f"  {wb.get('name', wb_id)} ({wb_id}){tag_str}")
            return

        for wb in workbooks:
            tags = wb_tags.get(wb["workbookId"], [])
            extract_workbook(client, wb, output_dir, tags=tags)
            print()

    print("Done.")


if __name__ == "__main__":
    main()
