"""Streamlit UI for Property Ops Copilot."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import get_settings  # noqa: E402
from src.data.bootstrap import ensure_database  # noqa: E402
from src.models import ChatRequest, ChatResponse  # noqa: E402
from src.pipeline.run import CopilotPipeline  # noqa: E402


def _apply_streamlit_secrets() -> None:
    for key in ("OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL", "USE_LLM", "DATABASE_PATH"):
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
    get_settings.cache_clear()


_apply_streamlit_secrets()
ensure_database(sample_only=True)

st.set_page_config(page_title="Property Ops Copilot", layout="wide")
st.title("Property Ops Copilot")
st.caption("Lease Q&A with citations · Maintenance tickets · Compliance guardrails")


def _db_mtime() -> float:
    path = get_settings().db_path
    return path.stat().st_mtime if path.exists() else 0.0


@st.cache_resource
def get_pipeline(db_mtime: float) -> CopilotPipeline:
    """Rebuild pipeline when property_ops.db changes (e.g. after init_data.py)."""
    _ = db_mtime
    return CopilotPipeline()


def format_assistant_reply(result: ChatResponse) -> str:
    """Plain-language reply with an inline citation when available."""
    lines = [result.response.message.strip()]

    if result.response.citations:
        cite = result.response.citations[0]
        lines.append("")
        lines.append(f"**Source:** Section {cite.section} — {cite.title}")

    if result.response.work_order_id and result.response.work_order_id not in result.response.message:
        lines.append("")
        lines.append(f"**Work order:** {result.response.work_order_id}")

    return "\n".join(lines)


if "messages" not in st.session_state:
    st.session_state.messages = []

pipeline = get_pipeline(_db_mtime())
units = pipeline.list_units()
unit_options = {f"{u['id']} ({u['property_name']} #{u['label']})": u["id"] for u in units}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Tenant context")
    unit_label = st.selectbox("Unit", options=list(unit_options.keys()))
    unit_id = unit_options[unit_label]
    session_id = st.text_input("Session ID", value="demo-session")

with col2:
    st.subheader("Conversation")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about your lease or report a maintenance issue...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        result = pipeline.handle(
            ChatRequest(session_id=session_id, message=prompt, unit_id=unit_id)
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": format_assistant_reply(result)}
        )
        st.rerun()
