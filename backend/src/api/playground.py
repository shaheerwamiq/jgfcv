"""Playground endpoints: chain demos, parser demos, embedding similarity."""

import time

from fastapi import APIRouter

from src.chains.conditional import run_conditional_chain
from src.chains.parallel import run_parallel_chain
from src.chains.parsers import run_pydantic_parser, run_str_parser
from src.chains.sequential import run_sequential_chain
from src.core.cache import response_cache
from src.core.observability import run_store
from src.llm.embeddings import get_embeddings, similarity_matrix
from src.schemas.models import (
    ChainDemoRequest,
    ChainDemoResponse,
    ParserDemoRequest,
    ParserDemoResponse,
    SimilarityRequest,
    SimilarityResponse,
)

router = APIRouter(tags=["playground"])


@router.post("/chains/demo", response_model=ChainDemoResponse)
def chain_demo(request: ChainDemoRequest) -> ChainDemoResponse:
    """Run one of the three chain patterns and return output + trace."""
    runners = {
        "sequential": run_sequential_chain,
        "conditional": run_conditional_chain,
        "parallel": run_parallel_chain,
    }
    output, steps, latency_ms = runners[request.chain_type](request.text)
    run_store.record("chain_demo", f"chain:{request.chain_type}", request.text, "ok", latency_ms, steps)
    return ChainDemoResponse(
        chain_type=request.chain_type,
        output=output,
        steps=steps,
        latency_ms=latency_ms,
    )


@router.post("/parsers/demo", response_model=ParserDemoResponse)
def parser_demo(request: ParserDemoRequest) -> ParserDemoResponse:
    """Compare StrOutputParser vs PydanticOutputParser on the same input."""
    if request.parser == "str":
        output, latency_ms = run_str_parser(request.text)
    else:
        output, latency_ms = run_pydantic_parser(request.text)
    run_store.record("parser_demo", f"parser:{request.parser}", request.text, "ok", latency_ms)
    return ParserDemoResponse(parser=request.parser, output=output, latency_ms=latency_ms)


@router.post("/embeddings/similarity", response_model=SimilarityResponse)
def similarity(request: SimilarityRequest) -> SimilarityResponse:
    """Embed texts and return the pairwise cosine similarity matrix (cached)."""
    start = time.time()
    key = response_cache.make_key("similarity", request.texts)
    cached = response_cache.get(key)
    if cached is not None:
        return SimilarityResponse(**cached, latency_ms=int((time.time() - start) * 1000))

    vectors = get_embeddings().embed_documents(request.texts)
    matrix = similarity_matrix(vectors)
    latency_ms = int((time.time() - start) * 1000)
    payload = {"texts": request.texts, "matrix": matrix, "dimensions": len(vectors[0])}
    response_cache.set(key, payload)
    run_store.record("similarity", "embeddings", " | ".join(request.texts), "ok", latency_ms)
    return SimilarityResponse(**payload, latency_ms=latency_ms)
