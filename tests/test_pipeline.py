from src.models import ChatRequest
from src.tools.registry import infer_maintenance_category


def test_lease_search_returns_citations(pipeline):
    result = pipeline.handle(
        ChatRequest(
            session_id="t1",
            message="What is the pet policy?",
            unit_id="UNIT-101",
        )
    )
    assert result.route.agent.value == "lease"
    assert result.response.citations
    assert "pet" in result.response.message.lower()


def test_maintenance_creates_work_order(pipeline):
    result = pipeline.handle(
        ChatRequest(
            session_id="t2",
            message="Bathroom faucet is leaking badly",
            unit_id="UNIT-204",
        )
    )
    assert result.route.agent.value == "maintenance"
    assert result.response.work_order_id
    assert result.response.work_order_id.startswith("WO-")


def test_infer_category():
    assert infer_maintenance_category("no heat in apartment") == "hvac"
    assert infer_maintenance_category("outlet sparking") == "electrical"
