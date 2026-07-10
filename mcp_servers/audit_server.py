"""Thin MCP wrapper for audit log access."""

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

mcp = FastMCP("audit-mcp")


@mcp.tool()
def recent_audit(limit: int = 20) -> str:
    """Return recent tool audit entries."""
    result = _tools.call("audit.recent", {"limit": limit}, agent="mcp-audit")
    return json.dumps(result.model_dump(), indent=2)


if __name__ == "__main__":
    asyncio.run(mcp.run())
