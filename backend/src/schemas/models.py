"""Pydantic request/response models for the public API.

Every boundary of the system is typed and validated: FastAPI uses these
for request validation, response serialisation, and OpenAPI docs.
"""

from typing import Literal

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------
# Shared
# --------------------------------------------------------------------------
class TraceStep(BaseModel):
    """One observable step of a workflow run (for the trace viewer UI)."""

    step: str
    agent: str
    detail: str
    latency_ms: int = 0
    status: Literal["ok", "blocked", "error", "skipped"] = "ok"


class GuardrailVerdict(BaseModel):
    """Result of running input/output guardrails."""

    passed: bool
    rail: str = ""
    reason: str = ""


# --------------------------------------------------------------------------
# Workflow (multi-agent)
# --------------------------------------------------------------------------
class WorkflowRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str = Field(default="default", max_length=64)


class WorkflowResponse(BaseModel):
    answer: str
    agent: str
    route_reason: str
    sources: list[str] = []
    trace: list[TraceStep] = []
    input_guardrail: GuardrailVerdict
    output_guardrail: GuardrailVerdict
    total_latency_ms: int


# --------------------------------------------------------------------------
# Documents / RAG
# --------------------------------------------------------------------------
class IngestTextRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=200_000)


class IngestResponse(BaseModel):
    name: str
    chunks: int
    characters: int
    avg_chunk_chars: int
    sample_chunks: list[str]


class DocumentInfo(BaseModel):
    name: str
    chunks: int
    characters: int


class RagQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class RetrievedChunk(BaseModel):
    content: str
    source: str
    score: float | None = None


class RagQueryResponse(BaseModel):
    answer: str
    chunks: list[RetrievedChunk]
    latency_ms: int


# --------------------------------------------------------------------------
# Playground: chains
# --------------------------------------------------------------------------
class ChainDemoRequest(BaseModel):
    chain_type: Literal["sequential", "conditional", "parallel"]
    text: str = Field(min_length=1, max_length=4000)


class ChainDemoResponse(BaseModel):
    chain_type: str
    output: dict
    steps: list[TraceStep]
    latency_ms: int


class ParserDemoRequest(BaseModel):
    parser: Literal["str", "pydantic"]
    text: str = Field(min_length=1, max_length=4000)


class ParserDemoResponse(BaseModel):
    parser: str
    output: dict | str
    latency_ms: int


# --------------------------------------------------------------------------
# Playground: embeddings
# --------------------------------------------------------------------------
class SimilarityRequest(BaseModel):
    texts: list[str] = Field(min_length=2, max_length=6)


class SimilarityResponse(BaseModel):
    texts: list[str]
    matrix: list[list[float]]
    dimensions: int
    latency_ms: int


# --------------------------------------------------------------------------
# Observability
# --------------------------------------------------------------------------
class RunSummary(BaseModel):
    run_id: str
    kind: str
    agent: str
    input_preview: str
    status: str
    total_latency_ms: int
    timestamp: float
    trace: list[TraceStep] = []


class ObservabilityResponse(BaseModel):
    runs: list[RunSummary]
    cache: dict
    totals: dict
