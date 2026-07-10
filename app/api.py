from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from src.models import ChatRequest, ChatResponse
from src.pipeline.run import CopilotPipeline

_pipeline: CopilotPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pipeline
    _pipeline = CopilotPipeline()
    yield
    if _pipeline:
        _pipeline.close()
        _pipeline = None


app = FastAPI(title="Property Ops Copilot", version="0.1.0", lifespan=lifespan)


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
