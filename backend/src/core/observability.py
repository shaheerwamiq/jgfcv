"""In-process run tracing (lightweight LangSmith/Logfire stand-in).

Every workflow/chain/RAG run is recorded with its trace steps so the UI
can show what happened, in what order, and how long each step took.
Production systems export these to LangSmith, Logfire, or OpenTelemetry;
the docs cover those integrations.
"""

import threading
import time
import uuid

from src.schemas.models import RunSummary, TraceStep

MAX_RUNS = 100


class RunStore:
    """Thread-safe ring buffer of recent run summaries."""

    def __init__(self) -> None:
        self._runs: list[RunSummary] = []
        self._lock = threading.Lock()

    def record(
        self,
        kind: str,
        agent: str,
        input_text: str,
        status: str,
        total_latency_ms: int,
        trace: list[TraceStep] | None = None,
    ) -> str:
        run = RunSummary(
            run_id=uuid.uuid4().hex[:12],
            kind=kind,
            agent=agent,
            input_preview=input_text[:120],
            status=status,
            total_latency_ms=total_latency_ms,
            timestamp=time.time(),
            trace=trace or [],
        )
        with self._lock:
            self._runs.append(run)
            if len(self._runs) > MAX_RUNS:
                del self._runs[: len(self._runs) - MAX_RUNS]
        return run.run_id

    def list_runs(self, limit: int = 50) -> list[RunSummary]:
        with self._lock:
            return list(reversed(self._runs[-limit:]))

    def totals(self) -> dict:
        with self._lock:
            if not self._runs:
                return {"runs": 0, "avg_latency_ms": 0, "errors": 0}
            errors = sum(1 for r in self._runs if r.status != "ok")
            avg = sum(r.total_latency_ms for r in self._runs) // len(self._runs)
            return {"runs": len(self._runs), "avg_latency_ms": avg, "errors": errors}


run_store = RunStore()
