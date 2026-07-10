from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentName(str, Enum):
    ROUTER = "router"
    LEASE = "lease"
    MAINTENANCE = "maintenance"
    COMPLIANCE = "compliance"


class TicketPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Citation(BaseModel):
    lease_id: str
    section: str
    title: str
    excerpt: str
    score: float = 0.0


class LeaseAnswer(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = 0.0


class WorkOrder(BaseModel):
    id: str
    unit_id: str
    category: str
    priority: TicketPriority
    status: TicketStatus
    description: str
    created_at: datetime


class ToolResult(BaseModel):
    ok: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class RouteDecision(BaseModel):
    agent: AgentName
    confidence: float
    reason: str


class ComplianceResult(BaseModel):
    requires_approval: bool
    is_urgent: bool
    flags: list[str] = Field(default_factory=list)
    sanitized_response: str | None = None


class AgentResponse(BaseModel):
    agent: AgentName
    message: str
    citations: list[Citation] = Field(default_factory=list)
    work_order_id: str | None = None
    requires_approval: bool = False
    approval_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str
    unit_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    route: RouteDecision
    response: AgentResponse
    compliance: ComplianceResult
