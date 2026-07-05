"""Research agent: answers questions grounded in the uploaded documents (RAG)."""

import time

from src.agents.state import WorkflowState
from src.core.errors import DocumentNotFoundError
from src.rag.pipeline import answer_question
from src.schemas.models import TraceStep


def research_node(state: WorkflowState) -> dict:
    """Retrieve relevant chunks, answer with citations, record the trace."""
    start = time.time()
    trace = state.get("trace", [])
    try:
        answer, results, _latency = answer_question(state["message"])
        sources = []
        for doc, _score in results:
            src = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page")
            tag = f"{src} (p.{page})" if page else src
            if tag not in sources:
                sources.append(tag)
        step = TraceStep(
            step="rag_answer",
            agent="research",
            detail=f"Retrieved {len(results)} chunks from {len(sources)} source(s), generated grounded answer",
            latency_ms=int((time.time() - start) * 1000),
        )
        return {"answer": answer, "sources": sources, "trace": trace + [step]}
    except DocumentNotFoundError:
        step = TraceStep(
            step="rag_answer",
            agent="research",
            detail="No documents indexed — nothing to retrieve",
            latency_ms=int((time.time() - start) * 1000),
            status="error",
        )
        return {
            "answer": "No documents have been ingested yet. Upload a document first, then ask again.",
            "sources": [],
            "trace": trace + [step],
        }
