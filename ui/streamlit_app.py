"""Streamlit UI for Property Ops Copilot."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models import ChatRequest  # noqa: E402
from src.pipeline.run import CopilotPipeline  # noqa: E402

st.set_page_config(page_title="Property Ops Copilot", layout="wide")
st.title("Property Ops Copilot")
st.caption("Lease Q&A with citations · Maintenance tickets · Compliance guardrails")

if "pipeline" not in st.session_state:
    st.session_state.pipeline = CopilotPipeline()
    st.session_state.messages = []

units = st.session_state.pipeline.list_units()
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
            if msg.get("meta"):
                with st.expander("Details"):
                    st.json(msg["meta"])

    prompt = st.chat_input("Ask about your lease or report a maintenance issue...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        result = st.session_state.pipeline.handle(
            ChatRequest(session_id=session_id, message=prompt, unit_id=unit_id)
        )
        meta = {
            "route": result.route.model_dump(),
            "compliance": result.compliance.model_dump(),
            "citations": [c.model_dump() for c in result.response.citations],
            "work_order_id": result.response.work_order_id,
            "approval_id": result.response.approval_id,
        }
        st.session_state.messages.append(
            {"role": "assistant", "content": result.response.message, "meta": meta}
        )
        st.rerun()
