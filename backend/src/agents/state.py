"""Shared state flowing through the LangGraph workflow.

LangGraph nodes read from and write partial updates to this TypedDict.
Keeping state explicit (instead of hidden in closures) is what makes
multi-agent systems debuggable.
"""

from typing import TypedDict

from src.schemas.models import TraceStep


class WorkflowState(TypedDict, total=False):
    """State record passed between supervisor and worker agents."""

    message: str            # original user request
    session_id: str         # chat session for history
    route: str              # supervisor's decision: research | analyst | writer
    route_reason: str       # why the supervisor chose that route
    answer: str             # final agent answer
    sources: list[str]      # citation sources (research agent)
    trace: list[TraceStep]  # accumulated observability steps
