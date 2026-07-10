from src.guardrails.compliance import evaluate_compliance


def test_flags_urgent_maintenance():
    result = evaluate_compliance("We have no heat in unit 101", "Ticket created.")
    assert result.is_urgent
    assert "urgent_maintenance" in result.flags


def test_requires_approval_for_legal_topics():
    result = evaluate_compliance("I want to talk to my attorney about mold", "Here is general info.")
    assert result.requires_approval
    assert "legal_or_safety_review" in result.flags


def test_blocks_unauthorized_promises():
    result = evaluate_compliance("Can I get a refund?", "You are evicted and we will refund everything.")
    assert result.sanitized_response is not None
    assert "property manager" in result.sanitized_response.lower()
