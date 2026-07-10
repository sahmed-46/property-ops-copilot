# Property Ops Copilot — Project Charter

**Owner:** Syed Omar Ahmed  
**Status:** MVP / Portfolio  
**Last updated:** July 2026

---

## 1. Summary

**Property Ops Copilot** is a multi-agent PropTech operations assistant that helps property managers answer lease questions, triage maintenance issues, and escalate compliance-sensitive cases. Specialist agents call **custom MCP servers** for lease retrieval, work order actions, and audit logging. The system is grounded (citations required), action-capable (ticket creation), and auditable (every tool call logged).

**One-line pitch:** *A property operations copilot that reads leases, creates tickets, and escalates safely—with a full audit trail.*

---

## 2. Problem

| Problem | Impact |
|---|---|
| Lease answers live in PDFs and are slow to find | PM time wasted, inconsistent tenant/owner responses |
| Maintenance requests are manually triaged | Delays, missed urgent issues, SLA risk |
| AI tools lack traceability | Leadership cannot trust or approve automation |
| Agent integrations are one-off API glue | Hard to scale new data sources and tools |

---

## 3. Why now

Property operators need workflow automation, not another chatbot. The market is moving toward **agentic systems with tool use (MCP)** and **human-in-the-loop** guardrails for regulated, liability-sensitive domains like real estate.

---

## 4. Goals (MVP)

| # | Goal | Success metric |
|---|---|---|
| G1 | Answer lease questions with citations | ≥80% correct on 15-scenario lease eval set |
| G2 | Create maintenance tickets from natural language | ≥90% correct priority + unit routing on 10 scenarios |
| G3 | Escalate safety/legal cases to human review | 100% recall on high-risk test cases (mold, legal threat, no heat) |
| G4 | Log every agent action via MCP audit server | 100% of tool calls recorded with timestamp + agent id |
| G5 | Demo-ready in one repo | README + 3–5 min video + Docker or clear setup steps |

---

## 5. Non-goals (v1)

- Real PMS integrations (Yardi, AppFolio, RealPage)
- Autonomous legal advice or auto-send to tenants without review
- Payments, evictions, or accounting workflows
- Mobile app and full enterprise RBAC
- Production SLA / multi-tenant hardening

---

## 6. Use cases (in scope)

1. **Lease Q&A** — renewal dates, notice clauses, repair obligations (with citations)
2. **Maintenance triage** — parse issue, set priority, create work order
3. **Compliance escalation** — flag mold, safety, legal; require human approval
4. **Ops trace view** — inspect MCP tool calls, latencies, and approval events

---

## 7. Scope

### Agents
- **Router** — intent classification and handoff
- **Lease** — RAG + MCP lease tools
- **Maintenance** — ticket creation and status lookup
- **Compliance** — policy checks and human-review gates
- **Comms** (optional MVP+) — draft tenant/PM messages from verified facts

### MCP servers (custom)
- `lease-mcp` — `search_clauses`, `list_key_dates`, `get_lease_metadata`
- `tickets-mcp` — `create_work_order`, `get_open_work_orders`, `update_status`
- `audit-mcp` — `log_action`, `require_human_approval`, `get_trace`

### Data (sample)
- 3 properties, 10 units, 10 tenants, 10 lease docs, 20 historical tickets

### UI
- Streamlit or simple web chat + audit/trace panel

---

## 8. Tech stack

| Layer | Choice |
|---|---|
| Backend | Python, FastAPI |
| Agents | LangGraph or custom supervisor |
| LLM | GPT-4o-mini / Claude Haiku |
| Structured outputs | Pydantic |
| MCP | Python MCP SDK |
| RAG | Qdrant or FAISS + sentence-transformers |
| Database | SQLite (MVP) → PostgreSQL (path to prod) |
| Docs | PDF ingestion (pypdf), chunked clauses |
| Tests | pytest (tools, routing, escalation rules) |
| Deploy | Docker Compose (optional) |

---

## 9. Milestones

| Week | Deliverable |
|---|---|
| **W1** | Sample data, lease ingestion, `lease-mcp` + `tickets-mcp` tools, unit tests |
| **W2** | Router + Lease + Maintenance agents, UC1 lease Q&A end-to-end |
| **W3** | Compliance agent, `audit-mcp`, UC2 maintenance flow, escalation eval |
| **W4** | Trace UI, README/architecture diagram, demo video, GitHub polish |

---

## 10. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Hallucinated lease answers | Citation required; reject uncited legal responses |
| Wrong maintenance priority | Rule layer + labeled eval set before demo |
| MCP/tool schema drift | Versioned tools + contract tests |
| Over-scope | Lock v1 to 2 user flows only |
| Production liability | Human approval for high-risk; assistive-only positioning in MVP |

---

## 11. Definition of done

- [ ] GitHub repo with setup instructions
- [ ] 3 MCP servers running locally
- [ ] 4 agents orchestrated with logged tool calls
- [ ] 2 demo flows working (lease Q&A + maintenance ticket)
- [ ] Eval doc with ≥15 scenarios and results table
- [ ] Architecture diagram in README
- [ ] 3–5 minute demo recording

---

## 12. Resume positioning

**Title:** Property Ops Copilot — Multi-Agent PropTech Assistant (Python, FastAPI, MCP, RAG)

**Target roles:** AI Engineer, Applied AI, Agentic workflows, Support/automation platforms

**Differentiator:** Custom MCP servers + multi-agent orchestration + audit trail (not a single LLM chat wrapper).
