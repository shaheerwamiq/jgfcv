"""Document ingestion + RAG query endpoints."""

import time

from fastapi import APIRouter, UploadFile

from src.core.errors import ValidationFailedError
from src.core.observability import run_store
from src.rag.loaders import load_pdf_bytes, load_text
from src.rag.pipeline import answer_question
from src.rag.splitter import chunk_stats, split_documents
from src.rag.vectorstore import vector_store
from src.schemas.models import (
    DocumentInfo,
    IngestResponse,
    IngestTextRequest,
    RagQueryRequest,
    RagQueryResponse,
    RetrievedChunk,
)

router = APIRouter(tags=["documents"])

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB


def _ingest(name: str, docs) -> IngestResponse:
    """Shared ingest path: split -> embed -> index -> stats."""
    chunks = split_documents(docs)
    if not chunks:
        raise ValidationFailedError("Document produced no chunks")
    vector_store.add_chunks(name, chunks)
    stats = chunk_stats(chunks)
    return IngestResponse(
        name=name,
        chunks=stats["chunks"],
        characters=stats["characters"],
        avg_chunk_chars=stats["avg_chunk_chars"],
        sample_chunks=[c.page_content[:220] for c in chunks[:3]],
    )


@router.post("/documents/ingest-text", response_model=IngestResponse)
def ingest_text(request: IngestTextRequest) -> IngestResponse:
    """Ingest pasted text: load -> split -> embed -> FAISS."""
    docs = load_text(request.name, request.content)
    return _ingest(request.name, docs)


@router.post("/documents/upload", response_model=IngestResponse)
async def upload(file: UploadFile) -> IngestResponse:
    """Ingest an uploaded .txt/.md/.pdf file."""
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValidationFailedError("File exceeds the 8 MB upload limit")
    name = file.filename or "upload"
    if name.lower().endswith(".pdf"):
        docs = load_pdf_bytes(name, data)
    else:
        try:
            docs = load_text(name, data.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ValidationFailedError("File is not valid UTF-8 text (only .txt, .md, .pdf supported)") from exc
    return _ingest(name, docs)


@router.get("/documents", response_model=list[DocumentInfo])
def list_documents() -> list[DocumentInfo]:
    """List all ingested documents."""
    return [DocumentInfo(**d) for d in vector_store.list_documents()]


@router.delete("/documents")
def reset_documents() -> dict:
    """Clear the entire vector index."""
    vector_store.reset()
    return {"status": "cleared"}


@router.post("/documents/query", response_model=RagQueryResponse)
def query(request: RagQueryRequest) -> RagQueryResponse:
    """Direct RAG query (retrieve -> augment -> generate) with chunk scores."""
    start = time.time()
    answer, results, _ = answer_question(request.question)
    latency_ms = int((time.time() - start) * 1000)
    run_store.record("rag_query", "research", request.question, "ok", latency_ms)
    return RagQueryResponse(
        answer=answer,
        chunks=[
            RetrievedChunk(
                content=doc.page_content[:400],
                source=str(doc.metadata.get("source", "unknown")),
                score=round(float(score), 4),
            )
            for doc, score in results
        ],
        latency_ms=latency_ms,
    )
