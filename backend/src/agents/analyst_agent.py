"""Analyst agent: structured analysis using a Pydantic-parsed chain.

Demonstrates production structured output inside an agent: the model must
return a schema-valid analysis, which we then render deterministically.
"""

import time

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.agents.state import WorkflowState
from src.llm.client import get_llm
from src.schemas.models import TraceStep


class Analysis(BaseModel):
    """Schema the analyst must produce."""

    headline: str = Field(description="One-line headline of the analysis")
    key_points: list[str] = Field(description="3-5 key analytical points")
    pros: list[str] = Field(description="Up to 3 advantages / positives")
    cons: list[str] = Field(description="Up to 3 disadvantages / risks")
    verdict: str = Field(description="2-3 sentence overall assessment")


ANALYST_PROMPT = ChatPromptTemplate.from_template(
    """You are a rigorous analyst. Analyze the following request thoroughly.

{format_instructions}

Request: {message}"""
)


def _render(analysis: Analysis) -> str:
    """Deterministic markdown rendering of the structured analysis."""
    lines = [f"## {analysis.headline}", "", "**Key points**"]
    lines += [f"- {p}" for p in analysis.key_points]
    if analysis.pros:
        lines += ["", "**Pros**"] + [f"- {p}" for p in analysis.pros]
    if analysis.cons:
        lines += ["", "**Cons**"] + [f"- {c}" for c in analysis.cons]
    lines += ["", f"**Verdict:** {analysis.verdict}"]
    return "\n".join(lines)


def analyst_node(state: WorkflowState) -> dict:
    """Run the structured analysis chain and record the trace."""
    start = time.time()
    trace = state.get("trace", [])
    parser = PydanticOutputParser(pydantic_object=Analysis)
    chain = (
        ANALYST_PROMPT.partial(format_instructions=parser.get_format_instructions())
        | get_llm(temperature=0.2)
        | parser
    )
    analysis: Analysis = chain.invoke({"message": state["message"]})
    step = TraceStep(
        step="structured_analysis",
        agent="analyst",
        detail=f"PydanticOutputParser produced schema-valid analysis with {len(analysis.key_points)} key points",
        latency_ms=int((time.time() - start) * 1000),
    )
    return {"answer": _render(analysis), "sources": [], "trace": trace + [step]}
