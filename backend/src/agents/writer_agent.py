"""Writer agent: general composition with session chat history.

Demonstrates the chat-history pattern from the notes: MessagesPlaceholder
injects prior turns so the model keeps conversational context.
"""

import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.agents.state import WorkflowState
from src.llm.client import get_llm
from src.memory.chat_history import history_store
from src.schemas.models import TraceStep

WRITER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a clear, helpful writer. Produce well-structured, concise "
            "responses. Use markdown formatting where it improves readability.",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{message}"),
    ]
)


def writer_node(state: WorkflowState) -> dict:
    """Compose a response with chat history context and record the trace."""
    start = time.time()
    trace = state.get("trace", [])
    session_id = state.get("session_id", "default")
    history = history_store.get(session_id)

    chain = WRITER_PROMPT | get_llm() | StrOutputParser()
    answer = chain.invoke({"message": state["message"], "history": history})

    step = TraceStep(
        step="compose",
        agent="writer",
        detail=f"Composed response with {len(history) // 2} prior exchange(s) of chat history",
        latency_ms=int((time.time() - start) * 1000),
    )
    return {"answer": answer, "sources": [], "trace": trace + [step]}
