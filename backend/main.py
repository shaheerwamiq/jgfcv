"""AgentForge backend entrypoint.

FastAPI app factory with:
- structured JSON logging
- domain-error -> HTTP mapping (no stack traces leak to clients)
- request logging middleware
- all routers mounted WITHOUT the /api prefix (Vercel strips it)
"""

import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.documents import router as documents_router
from src.api.playground import router as playground_router
from src.api.system import router as system_router
from src.api.workflows import router as workflows_router
from src.core.config import get_settings
from src.core.errors import AgentForgeError
from src.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging(debug=settings.debug)
logger = get_logger("app")

app = FastAPI(
    title="AgentForge API",
    description="Multi-agent AI workflow platform: LangChain + LangGraph + Gemini",
    version="1.0.0",
)


@app.exception_handler(AgentForgeError)
async def domain_error_handler(_request: Request, exc: AgentForgeError) -> JSONResponse:
    """Map domain errors to their HTTP status without leaking internals."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Catch-all: log the real error, return a safe generic message."""
    logger.error("unhandled exception", extra={"ctx": {"error": str(exc)}}, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "An internal error occurred"}},
    )


@app.middleware("http")
async def request_logging(request: Request, call_next):
    """Log every request with method, path, status, and latency."""
    start = time.time()
    response = await call_next(request)
    logger.info(
        "request",
        extra={
            "ctx": {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "latency_ms": int((time.time() - start) * 1000),
            }
        },
    )
    return response


app.include_router(system_router)
app.include_router(workflows_router)
app.include_router(documents_router)
app.include_router(playground_router)
