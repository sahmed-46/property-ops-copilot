from __future__ import annotations

from src.guardrails.compliance import evaluate_compliance
from src.models import AgentName, AgentResponse, ChatRequest, ChatResponse, RouteDecision
from src.agents.lease import run_lease_agent
from src.agents.maintenance import run_maintenance_agent
from src.agents.router import route_message
from src.db.connection import get_connection, init_schema
from src.db.repository import Repository
from src.retrieval.lease_index import LeaseIndex
from src.tools.registry import ToolRegistry


class CopilotPipeline:
    def __init__(self):
        init_schema()
        self.conn = get_connection()
        self.repo = Repository(self.conn)
        self.lease_index = LeaseIndex(self.repo.get_clauses())
        self.tools = ToolRegistry(self.repo, self.lease_index)

    def close(self) -> None:
        self.conn.close()

    def handle(self, request: ChatRequest) -> ChatResponse:
        route = route_message(request.message)

        if route.agent == AgentName.MAINTENANCE:
            response = run_maintenance_agent(
                request.message,
                self.tools,
                session_id=request.session_id,
                unit_id=request.unit_id,
            )
        else:
            response = run_lease_agent(
                request.message,
                self.tools,
                session_id=request.session_id,
                unit_id=request.unit_id,
            )

        compliance = evaluate_compliance(request.message, response.message)
        if compliance.sanitized_response:
            response.message = compliance.sanitized_response

        if compliance.requires_approval:
            approval_id = self.repo.create_approval(
                request.session_id,
                reason=", ".join(compliance.flags) or "policy_review",
                context={
                    "message": request.message,
                    "draft_response": response.message,
                    "agent": response.agent.value,
                },
            )
            response.requires_approval = True
            response.approval_id = approval_id
            response.message += (
                f"\n\nThis request requires manager review (ref: {approval_id})."
            )

        response.agent = AgentName.COMPLIANCE if compliance.requires_approval else response.agent
        return ChatResponse(
            session_id=request.session_id,
            route=route,
            response=response,
            compliance=compliance,
        )

    def list_units(self) -> list[dict]:
        return self.repo.list_units()
