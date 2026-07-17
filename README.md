# Property Ops Copilot

Multi-agent property operations assistant with **lease Q&A (cited retrieval)**, **maintenance ticketing**, **compliance guardrails**, and **thin MCP servers** over a shared tool registry.

## Architecture

```
property-ops-copilot/
├── configs/                 # App settings, escalation rules, dataset config
├── data/
│   ├── sample/              # Committed demo seed (seed.json)
│   ├── cache/               # Downloaded CSVs (gitignored, reused locally)
│   └── runtime/             # SQLite DB (gitignored)
├── src/
│   ├── data/                # Download, cache merge, DB seeding
│   ├── config.py            # Settings + YAML loaders
│   ├── models.py            # Pydantic schemas
│   ├── db/                  # SQLite schema + repository
│   ├── retrieval/           # TF-IDF lease clause index
│   ├── tools/registry.py    # Single source of truth for all tools
│   ├── guardrails/          # Urgent / approval / policy checks
│   ├── llm/                 # Optional OpenAI client (off by default)
│   ├── agents/              # Router, lease, maintenance specialists
│   └── pipeline/run.py      # Orchestrator: route → agent → compliance
├── mcp_servers/             # Thin MCP wrappers (lease, tickets, audit)
├── app/api.py               # FastAPI REST API
├── frontend/                # React + TypeScript chat UI (Vite)
├── ui/streamlit_app.py      # Streamlit demo UI
├── scripts/
│   ├── download_datasets.py # One-time fetch → data/cache/
│   └── init_data.py         # sample + cache → SQLite
└── tests/                   # Router, compliance, end-to-end flows
```

### Request flow

```
Tenant message
    → Router (keyword rules, optional LLM)
    → Lease agent (TF-IDF + citations) OR Maintenance agent (work order)
    → Compliance guardrails (urgent flag, human approval, response sanitization)
    → Audit log (every tool call)
```

### Design choices

| Layer | Approach |
|-------|----------|
| Tools | Implemented once in `ToolRegistry`; agents and MCP servers call the same handlers |
| Retrieval | scikit-learn TF-IDF over lease clauses (no external vector DB for demo) |
| Routing | Fast keyword classifier; optional LLM when `USE_LLM=true` |
| Storage | SQLite (swap path for Postgres in production) |
| MCP | Three thin servers exposing lease search, tickets, and audit |

## Quick start

```bash
cd property-ops-copilot
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Optional: download external datasets once (cached in data/cache/)
python scripts/download_datasets.py

# Build SQLite from sample + cache (works without download using sample only)
python scripts/init_data.py
pytest -q
```

`init_data.py` uses cached CSVs when present; otherwise it falls back to `data/sample/seed.json` only. The app never downloads data at runtime.

### Data workflow

```
download_datasets.py  →  data/cache/*.csv   (run once, or --force to refresh)
init_data.py          →  data/runtime/property_ops.db
app / Streamlit       →  reads DB only
```

### React UI (TypeScript)

```bash
# Terminal 1 — API
uvicorn app.api:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` to the FastAPI backend.

### Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

Try:
- **Lease:** "How much notice do I need to renew?" (unit UNIT-101)
- **Maintenance:** "Kitchen sink is leaking" (unit UNIT-204)
- **Compliance:** mention "mold" or "attorney" to trigger manager review

### FastAPI

```bash
uvicorn app.api:app --reload --port 8000
```

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"s1\",\"message\":\"pet policy?\",\"unit_id\":\"UNIT-101\"}"
```

### MCP servers (optional)

```bash
python mcp_servers/lease_server.py
python mcp_servers/tickets_server.py
python mcp_servers/audit_server.py
```

## Optional LLM routing

Copy `.env.example` to `.env` and set:

```
OPENAI_API_KEY=sk-...
USE_LLM=true
```

Without an API key the system runs fully offline using keyword routing and retrieval-based answers.

## License

MIT
