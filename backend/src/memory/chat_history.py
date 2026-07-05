"""Session-scoped chat history.

Implements the pattern from the course notes: maintain a rolling list of
(human, ai) messages per session and inject it into prompts via
MessagesPlaceholder so the model has conversational context.

In production this would live in Redis or Postgres keyed by session id;
the interface here (get / append / clear) is designed so that swap is
trivial.
"""

import threading

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

MAX_TURNS = 10  # keep the last N exchanges to bound token usage


class ChatHistoryStore:
    """Thread-safe in-memory chat history keyed by session id."""

    def __init__(self) -> None:
        self._sessions: dict[str, list[BaseMessage]] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> list[BaseMessage]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def append_exchange(self, session_id: str, human: str, ai: str) -> None:
        with self._lock:
            history = self._sessions.setdefault(session_id, [])
            history.append(HumanMessage(content=human))
            history.append(AIMessage(content=ai))
            # Trim to the last MAX_TURNS exchanges (2 messages per turn).
            if len(history) > MAX_TURNS * 2:
                del history[: len(history) - MAX_TURNS * 2]

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)


# Module-level singleton.
history_store = ChatHistoryStore()
