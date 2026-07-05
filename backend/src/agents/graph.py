"""LangGraph workflow assembly: supervisor -> conditional edge -> worker -> END.

    START -> supervisor --(route)--> research | analyst | writer -> END

This is the difference between LangChain and LangGraph in one file:
chains are linear pipes; graphs have state, branching, and (if needed)
cycles. See docs/knowledge-base/07-agents-langchain-vs-langgraph.md.
"""

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from src.agents.analyst_agent import analyst_node
from src.agents.research_agent import research_node
from src.agents.state import WorkflowState
from src.agents.supervisor import supervisor_node
from src.agents.writer_agent import writer_node


def route_to_agent(state: WorkflowState) -> str:
    """Conditional-edge function: reads the supervisor's decision."""
    return state.get("route", "writer")


@lru_cache
def build_graph():
    """Compile the multi-agent workflow graph (cached — it is immutable)."""
    graph = StateGraph(WorkflowState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("research", research_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("writer", writer_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {"research": "research", "analyst": "analyst", "writer": "writer"},
    )
    graph.add_edge("research", END)
    graph.add_edge("analyst", END)
    graph.add_edge("writer", END)

    return graph.compile()


def run_workflow(message: str, session_id: str = "default") -> WorkflowState:
    """Execute one workflow run through the compiled graph."""
    app = build_graph()
    initial: WorkflowState = {
        "message": message,
        "session_id": session_id,
        "trace": [],
    }
    return app.invoke(initial)
