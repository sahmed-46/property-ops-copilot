# React UI

TypeScript + React chat client for Property Ops Copilot. Calls the FastAPI backend at `/units` and `/chat`.

## Prerequisites

- Node.js 20+
- FastAPI running on port 8000 (see root README)

## Development

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api/*` to `http://127.0.0.1:8000`.

In another terminal:

```bash
cd ..
python scripts/init_data.py
uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
```

## Production build

```bash
npm run build
npm run preview
```

Set `VITE_API_BASE` when the API is hosted on a different origin:

```bash
VITE_API_BASE=https://api.example.com npm run build
```
