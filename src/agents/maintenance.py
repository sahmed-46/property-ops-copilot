from __future__ import annotations

from src.config import load_escalation_rules
from src.models import AgentName, AgentResponse, TicketPriority
from src.tools.registry import ToolRegistry, infer_maintenance_category


def run_maintenance_agent(
    message: str,
    tools: ToolRegistry,
    *,
    session_id: str,
    unit_id: str | None,
) -> AgentResponse:
    if not unit_id:
        return AgentResponse(
            agent=AgentName.MAINTENANCE,
            message="Please provide your unit ID so I can create a maintenance ticket.",
        )

    category = infer_maintenance_category(message)
    priority = _infer_priority(message)

    result = tools.call(
        "tickets.create",
        {
            "unit_id": unit_id,
            "description": message.strip(),
            "category": category,
            "priority": priority.value,
        },
        session_id=session_id,
        agent=AgentName.MAINTENANCE.value,
    )
    if not result.ok:
        return AgentResponse(agent=AgentName.MAINTENANCE, message=result.error or "Ticket creation failed.")

    wo_id = result.data["id"]
    msg = (
        f"Work order {wo_id} created for unit {unit_id} "
        f"({category}, {priority.value} priority). Our team will follow up shortly."
    )
    if priority == TicketPriority.URGENT:
        msg += " This has been flagged as urgent."

    return AgentResponse(
        agent=AgentName.MAINTENANCE,
        message=msg,
        work_order_id=wo_id,
        metadata={"category": category, "priority": priority.value},
    )


def _infer_priority(message: str) -> TicketPriority:
    rules = load_escalation_rules()
    text = message.lower()
    if any(kw in text for kw in rules.get("urgent_keywords", [])):
        return TicketPriority.URGENT
    if any(w in text for w in ("asap", "urgent", "emergency", "immediately")):
        return TicketPriority.HIGH
    return TicketPriority.NORMAL
