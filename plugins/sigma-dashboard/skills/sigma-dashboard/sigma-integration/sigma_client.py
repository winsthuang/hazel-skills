"""Sigma Computing REST API v2 client.

Handles authentication (client credentials), token refresh, pagination,
and the endpoints needed to extract SQL from workbook elements.
"""

from __future__ import annotations

import base64
import os
import time
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

# How many seconds before actual expiry to trigger a refresh
_TOKEN_REFRESH_BUFFER = 60


class SigmaClient:
    """Thin wrapper around the Sigma v2 REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        self.base_url = (base_url or os.environ["SIGMA_BASE_URL"]).rstrip("/")
        self._client_id = client_id or os.environ["SIGMA_CLIENT_ID"]
        self._client_secret = client_secret or os.environ["SIGMA_CLIENT_SECRET"]

        self._access_token: str | None = None
        self._token_expires_at: float = 0

        self._http = httpx.Client(timeout=30)

    # ── Auth ────────────────────────────────────────────────────────────

    def _ensure_token(self) -> None:
        """Fetch or refresh the bearer token when needed."""
        if self._access_token and time.time() < self._token_expires_at:
            return

        creds = base64.b64encode(
            f"{self._client_id}:{self._client_secret}".encode()
        ).decode()

        resp = self._http.post(
            f"{self.base_url}/v2/auth/token",
            headers={
                "Authorization": f"Basic {creds}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )
        resp.raise_for_status()
        body = resp.json()

        self._access_token = body["access_token"]
        self._token_expires_at = time.time() + body.get("expires_in", 3600) - _TOKEN_REFRESH_BUFFER

    def _headers(self) -> dict[str, str]:
        self._ensure_token()
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }

    # ── Generic helpers ─────────────────────────────────────────────────

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Authenticated GET returning the parsed JSON body."""
        resp = self._http.get(
            f"{self.base_url}{path}",
            headers=self._headers(),
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    def _paginate(self, path: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Follow nextPage tokens and collect all entries from a list endpoint."""
        params = dict(params or {})
        params.setdefault("limit", 100)
        items: list[dict[str, Any]] = []

        while True:
            body = self._get(path, params)
            items.extend(body.get("entries", []))

            next_page = body.get("nextPage")
            if not next_page:
                break
            params["page"] = next_page

        return items

    # ── Workbooks ───────────────────────────────────────────────────────

    def list_workbooks(self) -> list[dict[str, Any]]:
        """Return all workbooks the service account can see."""
        return self._paginate("/v2/workbooks")

    def get_workbook(self, workbook_id: str) -> dict[str, Any]:
        return self._get(f"/v2/workbooks/{workbook_id}")

    # ── Pages ───────────────────────────────────────────────────────────

    def list_pages(self, workbook_id: str) -> list[dict[str, Any]]:
        return self._paginate(f"/v2/workbooks/{workbook_id}/pages")

    # ── Elements ────────────────────────────────────────────────────────

    def list_elements(self, workbook_id: str, page_id: str) -> list[dict[str, Any]]:
        return self._paginate(f"/v2/workbooks/{workbook_id}/pages/{page_id}/elements")

    # ── Members ──────────────────────────────────────────────────────────

    def get_member(self, member_id: str) -> dict[str, Any]:
        """Return details for a specific member."""
        return self._get(f"/v2/members/{member_id}")

    def list_members(self) -> list[dict[str, Any]]:
        """Return all members."""
        return self._paginate("/v2/members")

    # ── Tags ────────────────────────────────────────────────────────────

    def list_tags(self) -> list[dict[str, Any]]:
        """Return all tags."""
        return self._paginate("/v2/tags")

    def get_workbook_tags(self, workbook_id: str) -> list[dict[str, Any]]:
        """Return tags for a specific workbook."""
        return self._paginate(f"/v2/workbooks/{workbook_id}/tags")

    # ── Queries / SQL ───────────────────────────────────────────────────

    def get_element_query(self, workbook_id: str, element_id: str) -> dict[str, Any]:
        """Return the compiled SQL for a single element.

        Response typically contains:
          - sql: the compiled SQL string
          - elementId, name, columns, etc.
        """
        return self._get(f"/v2/workbooks/{workbook_id}/elements/{element_id}/query")

    def list_queries(self, workbook_id: str) -> list[dict[str, Any]]:
        """Return all SQL queries across every element in a workbook."""
        return self._paginate(f"/v2/workbooks/{workbook_id}/queries")

    def get_element_columns(self, workbook_id: str, element_id: str) -> list[dict[str, Any]]:
        """Return column metadata for an element."""
        return self._paginate(f"/v2/workbooks/{workbook_id}/elements/{element_id}/columns")

    # ── Cleanup ─────────────────────────────────────────────────────────

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> SigmaClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
