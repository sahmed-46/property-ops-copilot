from __future__ import annotations

import re
from typing import Callable

from src.db.repository import Repository
from src.models import AgentName, LeaseAnswer, TicketPriority, ToolResult
from src.retrieval.lease_index import LeaseIndex


class ToolRegistry:
    """Single source of truth for lease, ticket, and audit operations."""

    def __init__(self, repo: Repository, lease_index: LeaseIndex):
        self.repo = repo
        self.lease_index = lease_index
        self._handlers: dict[str, Callable[..., ToolResult]] = {
            "lease.search": self._lease_search,
            "lease.get": self._lease_get,
            "tickets.create": self._tickets_create,
            "tickets.get": self._tickets_get,
            "audit.recent": self._audit_recent,
        }

    def call(
        self,
        tool: str,
        payload: dict,
        *,
        session_id: str = "default",
        agent: str = AgentName.LEASE.value,
    ) -> ToolResult:
        handler = self._handlers.get(tool)
        if not handler:
            return ToolResult(ok=False, error=f"Unknown tool: {tool}")
        result = handler(**payload)
        self.repo.log_audit(session_id, agent, tool, payload, result.model_dump())
        return result

    def _lease_search(self, query: str, unit_id: str | None = None) -> ToolResult:
        lease_id = None
        if unit_id:
            lease = self.repo.get_lease_for_unit(unit_id)
            lease_id = lease["id"] if lease else None
        citations = self.lease_index.search(query, lease_id=lease_id)
        answer = _compose_lease_answer(query, citations)
        return ToolResult(
            ok=True,
            data=LeaseAnswer(
                answer=answer,
                citations=citations,
                confidence=min(0.95, 0.4 + 0.15 * len(citations)),
            ).model_dump(),
        )

    def _lease_get(self, unit_id: str) -> ToolResult:
        lease = self.repo.get_lease_for_unit(unit_id)
        if not lease:
            return ToolResult(ok=False, error=f"No lease for unit {unit_id}")
        return ToolResult(ok=True, data=lease)

    def _tickets_create(
        self,
        unit_id: str,
        description: str,
        category: str = "general",
        priority: str = "normal",
    ) -> ToolResult:
        if not self.repo.get_unit(unit_id):
            return ToolResult(ok=False, error=f"Unknown unit: {unit_id}")
        wo = self.repo.create_work_order(
            unit_id=unit_id,
            category=category,
            priority=TicketPriority(priority),
            description=description,
        )
        return ToolResult(ok=True, data=wo.model_dump(mode="json"))

    def _tickets_get(self, work_order_id: str) -> ToolResult:
        wo = self.repo.get_work_order(work_order_id)
        if not wo:
            return ToolResult(ok=False, error=f"Work order not found: {work_order_id}")
        return ToolResult(ok=True, data=wo.model_dump(mode="json"))

    def _audit_recent(self, limit: int = 10) -> ToolResult:
        return ToolResult(ok=True, data={"entries": self.repo.recent_audit(limit)})


def _compose_lease_answer(query: str, citations: list) -> str:
    if not citations:
        return (
            "I couldn't find a lease clause that answers that question. "
            "Try mentioning your unit number or using words like pets, renewal, or maintenance."
        )
    return citations[0].excerpt.strip()


_MAINTENANCE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(leak\w*|drip\w*)\b", re.I), "plumbing"),
    (re.compile(r"\b(heat|heater|furnace|hvac|ac|air conditioning)\b", re.I), "hvac"),
    (re.compile(r"\b(electric|outlet|power|light)\b", re.I), "electrical"),
    (re.compile(r"\b(appliance|dishwasher|oven|fridge)\b", re.I), "appliance"),
]


def infer_maintenance_category(text: str) -> str:
    for pattern, category in _MAINTENANCE_PATTERNS:
        if pattern.search(text):
            return category
    return "general"
