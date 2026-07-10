"""Thin MCP wrapper over the shared tool registry."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from src.db.connection import get_connection, init_schema  # noqa: E402
from src.db.repository import Repository  # noqa: E402
from src.retrieval.lease_index import LeaseIndex  # noqa: E402
from src.tools.registry import ToolRegistry  # noqa: E402

init_schema()
_conn = get_connection()
_repo = Repository(_conn)
_tools = ToolRegistry(_repo, LeaseIndex(_repo.get_clauses()))

mcp = FastMCP("lease-mcp")


@mcp.tool()
def search_lease(query: str, unit_id: str | None = None) -> str:
    """Search lease clauses and return cited answer."""
    result = _tools.call("lease.search", {"query": query, "unit_id": unit_id}, agent="mcp-lease")
    return json.dumps(result.model_dump(), indent=2)


@mcp.tool()
def get_lease(unit_id: str) -> str:
    """Get active lease metadata for a unit."""
    result = _tools.call("lease.get", {"unit_id": unit_id}, agent="mcp-lease")
    return json.dumps(result.model_dump(), indent=2)


if __name__ == "__main__":
    asyncio.run(mcp.run())
