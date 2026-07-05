"""Sequential chain: output of step 1 feeds step 2 (LCEL pipe composition).

Pattern from the notes:
    chain = prompt1 | llm | parser | prompt2 | llm | parser
Here: text -> detailed report -> 3-bullet summary.
"""

import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.llm.client import get_llm
from src.schemas.models import TraceStep


def run_sequential_chain(text: str) -> tuple[dict, list[TraceStep], int]:
    """Two-stage pipeline; returns intermediate + final output for the UI."""
    start = time.time()
    llm = get_llm()
    parser = StrOutputParser()

    report_prompt = ChatPromptTemplate.from_template(
        "Write a short, detailed report (4-6 sentences) on the topic: {topic}"
    )
    summary_prompt = ChatPromptTemplate.from_template(
        "Summarize the following report as exactly 3 bullet points:\n\n{report}"
    )

    # Stage 1
    t1 = time.time()
    report = (report_prompt | llm | parser).invoke({"topic": text})
    stage1_ms = int((time.time() - t1) * 1000)

    # Stage 2 — consumes stage 1 output
    t2 = time.time()
    summary = (summary_prompt | llm | parser).invoke({"report": report})
    stage2_ms = int((time.time() - t2) * 1000)

    steps = [
        TraceStep(step="generate_report", agent="chain:sequential", detail="prompt1 | llm | StrOutputParser", latency_ms=stage1_ms),
        TraceStep(step="summarize_report", agent="chain:sequential", detail="prompt2 | llm | StrOutputParser (input = stage 1 output)", latency_ms=stage2_ms),
    ]
    output = {"report": report, "summary": summary}
    return output, steps, int((time.time() - start) * 1000)
