"""Supervisor: classifies the request and routes to a worker agent.

The supervisor pattern is the canonical LangGraph multi-agent design —
one cheap classification call decides which specialist handles the work.
Routing uses structured output (Pydantic) so the decision is machine-safe.
"""

import time
from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.agents.state import WorkflowState
from src.llm.client import get_llm
from src.rag.vectorstore import vector_store
from src.schemas.models import TraceStep


class RouteDecision(BaseModel):
    """Structured routing output — Literal constrains it to valid routes."""

    route: Literal["research", "analyst", "writer"] = Field(
        description="Which specialist agent should handle this request"
    )
    reason: str = Field(description="One sentence explaining the routing decision")


SUPERVISOR_PROMPT = ChatPromptTemplate.from_template(
    """You are a supervisor routing requests to specialist agents.

Agents:
- research: answers questions using the user's uploaded documents (RAG). \
Choose this for questions about specific documents or "what does the doc say" style requests. \
Documents currently indexed: {has_docs}.
- analyst: performs structured analysis — sentiment, classification, comparisons, \
pros/cons, breakdowns of a topic or text.
- writer: composes content — summaries, emails, articles, explanations, general questions.

{format_instructions}

User request: {message}"""
)


def supervisor_node(state: WorkflowState) -> dict:
    """Classify the request and record the routing decision in the trace."""
    start = time.time()
    parser = PydanticOutputParser(pydantic_object=RouteDecision)
    has_docs = "yes" if not vector_store.is_empty else "no (route document questions to writer instead)"

    chain = (
        SUPERVISOR_PROMPT.partial(format_instructions=parser.get_format_instructions())
        | get_llm(temperature=0.0)
        | parser
    )
    try:
        decision: RouteDecision = chain.invoke({"message": state["message"], "has_docs": has_docs})
        route, reason = decision.route, decision.reason
    except Exception:
        # Fail open to the most general agent rather than erroring the run.
        route, reason = "writer", "Routing classification failed; defaulted to writer"

    # Never route to research when the index is empty.
    if route == "research" and vector_store.is_empty:
        route, reason = "writer", "No documents indexed; rerouted from research to writer"

    step = TraceStep(
        step="route",
        agent="supervisor",
        detail=f"Routed to '{route}': {reason}",
        latency_ms=int((time.time() - start) * 1000),
    )
    return {"route": route, "route_reason": reason, "trace": state.get("trace", []) + [step]}
