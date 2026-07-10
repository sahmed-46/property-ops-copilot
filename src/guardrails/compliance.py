from __future__ import annotations

from src.config import load_escalation_rules
from src.models import ComplianceResult


def evaluate_compliance(message: str, draft_response: str) -> ComplianceResult:
    rules = load_escalation_rules()
    text = f"{message} {draft_response}".lower()

    urgent = [kw for kw in rules.get("urgent_keywords", []) if kw in text]
    approval = [kw for kw in rules.get("human_approval_keywords", []) if kw in text]
    blocked = [p for p in rules.get("blocked_response_patterns", []) if p in draft_response.lower()]

    flags = []
    if urgent:
        flags.append("urgent_maintenance")
    if approval:
        flags.append("legal_or_safety_review")
    if blocked:
        flags.append("policy_violation")

    sanitized = draft_response
    if blocked:
        sanitized = (
            "I cannot confirm that outcome. A property manager will review your request "
            "and follow up with accurate information."
        )

    return ComplianceResult(
        requires_approval=bool(approval or blocked),
        is_urgent=bool(urgent),
        flags=flags,
        sanitized_response=sanitized if sanitized != draft_response else None,
    )
