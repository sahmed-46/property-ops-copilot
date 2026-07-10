from __future__ import annotations

from src.models import AgentName, AgentResponse, Citation, LeaseAnswer
from src.tools.registry import ToolRegistry


def run_lease_agent(
    message: str,
    tools: ToolRegistry,
    *,
    session_id: str,
    unit_id: str | None,
) -> AgentResponse:
    result = tools.call(
        "lease.search",
        {"query": message, "unit_id": unit_id},
        session_id=session_id,
        agent=AgentName.LEASE.value,
    )
    if not result.ok:
        return AgentResponse(agent=AgentName.LEASE, message=result.error or "Lease lookup failed.")

    answer = LeaseAnswer.model_validate(result.data)
    citations = [Citation.model_validate(c) for c in result.data.get("citations", [])]
    return AgentResponse(
        agent=AgentName.LEASE,
        message=answer.answer,
        citations=citations or answer.citations,
        metadata={"confidence": answer.confidence},
    )
