"""Parallel chain: RunnableParallel fans out to independent chains at once.

Pattern from the notes:
    parallel = RunnableParallel(notes=chain1, quiz=chain2)
Independent branches run concurrently, so wall-clock time is roughly
max(branch latencies) instead of their sum.
"""

import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel

from src.llm.client import get_llm
from src.schemas.models import TraceStep


def run_parallel_chain(text: str) -> tuple[dict, list[TraceStep], int]:
    """Fan out into notes + quiz + key-terms branches simultaneously."""
    start = time.time()
    llm = get_llm()
    parser = StrOutputParser()

    notes_chain = (
        ChatPromptTemplate.from_template("Create concise study notes (4-5 bullets) on: {text}")
        | llm
        | parser
    )
    quiz_chain = (
        ChatPromptTemplate.from_template("Write 3 short quiz questions (with answers) about: {text}")
        | llm
        | parser
    )
    terms_chain = (
        ChatPromptTemplate.from_template("List the 5 most important terms in '{text}', each with a one-line definition.")
        | llm
        | parser
    )

    parallel = RunnableParallel(notes=notes_chain, quiz=quiz_chain, key_terms=terms_chain)

    t1 = time.time()
    result = parallel.invoke({"text": text})
    parallel_ms = int((time.time() - t1) * 1000)

    steps = [
        TraceStep(step="fan_out", agent="chain:parallel", detail="RunnableParallel(notes, quiz, key_terms) — 3 branches run concurrently", latency_ms=0),
        TraceStep(step="join_results", agent="chain:parallel", detail=f"All branches completed; wall-clock ≈ max(branch latency) = {parallel_ms}ms", latency_ms=parallel_ms),
    ]
    return dict(result), steps, int((time.time() - start) * 1000)
