from __future__ import annotations

import json
from typing import Any

import httpx

from src.config import get_settings


def chat_completion(system: str, user: str) -> str | None:
    settings = get_settings()
    if not settings.llm_enabled:
        return None

    url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    payload: dict[str, Any] = {
        "model": settings.openai_model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, json.JSONDecodeError):
        return None
