from __future__ import annotations

import re

from src.config import load_app_config
from src.llm.client import chat_completion
from src.models import AgentName, RouteDecision

_LEASE_HINTS = re.compile(
    r"\b(lease|rent|renewal|notice|deposit|pet|sublet|terminate|clause|move[- ]?out|"
    r"parking|guest|noise|insurance|utility|utilities|smok\w*|key|keys|storage|cleaning)\b",
    re.I,
)
_MAINT_HINTS = re.compile(
    r"\b(broken|repair|fix|maintenance|ticket|work order|leak\w*|heat|hvac|plumb\w*|outlet|"
    r"mold|pest|roach|clog|clogged|ac|heater|faucet|toilet)\b",
    re.I,
)


def route_message(message: str) -> RouteDecision:
    lease_score = len(_LEASE_HINTS.findall(message))
    maint_score = len(_MAINT_HINTS.findall(message))

    if lease_score == 0 and maint_score == 0:
        llm_route = _llm_route(message)
        if llm_route:
            return llm_route
        return RouteDecision(
            agent=AgentName.LEASE,
            confidence=0.45,
            reason="Defaulting to lease agent; message was ambiguous.",
        )

    if maint_score > lease_score:
        return RouteDecision(
            agent=AgentName.MAINTENANCE,
            confidence=min(0.95, 0.55 + 0.1 * maint_score),
            reason="Maintenance keywords detected.",
        )

    return RouteDecision(
        agent=AgentName.LEASE,
        confidence=min(0.95, 0.55 + 0.1 * lease_score),
        reason="Lease or policy keywords detected.",
    )


def _llm_route(message: str) -> RouteDecision | None:
    cfg = load_app_config().get("routing", {})
    raw = chat_completion(
        "Classify tenant message as lease or maintenance. Reply JSON: "
        '{"agent":"lease"|"maintenance","confidence":0-1,"reason":"..."}',
        message,
    )
    if not raw:
        return None
    try:
        import json

        data = json.loads(raw.strip().strip("`").split("\n", 1)[-1])
        agent = AgentName.LEASE if data.get("agent") == "lease" else AgentName.MAINTENANCE
        conf = float(data.get("confidence", 0.6))
        if conf < cfg.get("confidence_threshold", 0.55):
            return None
        return RouteDecision(agent=agent, confidence=conf, reason=data.get("reason", "LLM routing"))
    except (json.JSONDecodeError, ValueError, KeyError):
        return None
