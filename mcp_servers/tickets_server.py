"""Thin MCP wrapper for maintenance tickets."""

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

mcp = FastMCP("tickets-mcp")


@mcp.tool()
def create_ticket(
    unit_id: str,
    description: str,
    category: str = "general",
    priority: str = "normal",
) -> str:
    """Create a maintenance work order."""
    result = _tools.call(
        "tickets.create",
        {"unit_id": unit_id, "description": description, "category": category, "priority": priority},
        agent="mcp-tickets",
    )
    return json.dumps(result.model_dump(), indent=2)


@mcp.tool()
def get_ticket(work_order_id: str) -> str:
    """Fetch work order by ID."""
    result = _tools.call("tickets.get", {"work_order_id": work_order_id}, agent="mcp-tickets")
    return json.dumps(result.model_dump(), indent=2)


if __name__ == "__main__":
    asyncio.run(mcp.run())
