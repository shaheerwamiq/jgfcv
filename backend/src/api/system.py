"""Health + observability endpoints."""

from fastapi import APIRouter

from src.core.cache import response_cache
from src.core.config import get_settings
from src.core.observability import run_store
from src.rag.vectorstore import vector_store
from src.schemas.models import ObservabilityResponse

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict:
    """Liveness + config summary (no secrets)."""
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "api_key_configured": bool(settings.google_api_key),
        "guardrails_enabled": settings.guardrails_enabled,
        "documents_indexed": len(vector_store.list_documents()),
    }


@router.get("/observability", response_model=ObservabilityResponse)
def observability(limit: int = 50) -> ObservabilityResponse:
    """Recent runs + cache stats for the trace viewer UI."""
    return ObservabilityResponse(
        runs=run_store.list_runs(limit=min(limit, 100)),
        cache=response_cache.stats(),
        totals=run_store.totals(),
    )
