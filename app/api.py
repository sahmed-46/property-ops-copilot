from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.data.bootstrap import ensure_database
from src.models import ChatRequest, ChatResponse
from src.pipeline.run import CopilotPipeline

_pipeline: CopilotPipeline | None = None


def _cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pipeline
    ensure_database(sample_only=True)
    _pipeline = CopilotPipeline()
    yield
    if _pipeline:
        _pipeline.close()
        _pipeline = None


app = FastAPI(title="Property Ops Copilot", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/units")
def list_units() -> list[dict]:
    if not _pipeline:
        raise HTTPException(503, "Pipeline not ready")
    return _pipeline.list_units()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not _pipeline:
        raise HTTPException(503, "Pipeline not ready")
    if not request.message.strip():
        raise HTTPException(400, "Message cannot be empty")
    return _pipeline.handle(request)


api_router = APIRouter(prefix="/api")


@api_router.get("/health")
def api_health() -> dict:
    return health()


@api_router.get("/units")
def api_list_units() -> list[dict]:
    return list_units()


@api_router.post("/chat", response_model=ChatResponse)
def api_chat(request: ChatRequest) -> ChatResponse:
    return chat(request)


app.include_router(api_router)


def _register_frontend() -> None:
    from pathlib import Path

    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles

    static_dir = Path(__file__).resolve().parents[1] / "frontend" / "dist"
    if not static_dir.exists():
        return

    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    index_file = static_dir / "index.html"

    @app.get("/", include_in_schema=False)
    def serve_root() -> FileResponse:
        return FileResponse(index_file)

    @app.get("/{spa_path:path}", include_in_schema=False)
    def serve_spa(spa_path: str) -> FileResponse:
        if spa_path.startswith("assets/"):
            raise HTTPException(404)
        candidate = static_dir / spa_path
        if spa_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index_file)


_register_frontend()
