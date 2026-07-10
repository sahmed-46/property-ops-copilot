from src.agents.router import route_message
from src.models import AgentName


def test_routes_lease_questions():
    decision = route_message("How many days notice do I need to renew my lease?")
    assert decision.agent == AgentName.LEASE
    assert decision.confidence >= 0.55


def test_routes_maintenance_requests():
    decision = route_message("The kitchen sink is leaking and needs a repair ticket.")
    assert decision.agent == AgentName.MAINTENANCE
