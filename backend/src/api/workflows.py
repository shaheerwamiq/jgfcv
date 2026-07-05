"""Workflow endpoint: guardrails -> LangGraph multi-agent run -> guardrails."""

import time

from fastapi import APIRouter

from src.agents.graph import run_workflow
from src.core.observability import run_store
from src.guardrails.input_rails import check_input
from src.guardrails.output_rails import check_output
from src.memory.chat_history import history_store
from src.schemas.models import GuardrailVerdict, TraceStep, WorkflowRequest, WorkflowResponse

router = APIRouter(tags=["workflows"])


@router.post("/workflows/run", response_model=WorkflowResponse)
def run(request: WorkflowRequest) -> WorkflowResponse:
    """Execute one multi-agent workflow run with full guardrails + tracing."""
    start = time.time()

    # 1. Input guardrails (before any LLM spend).
    input_verdict = check_input(request.message)
    if not input_verdict.passed:
        blocked_step = TraceStep(
            step="input_guardrail", agent="guardrails",
            detail=input_verdict.reason, status="blocked",
        )
        total_ms = int((time.time() - start) * 1000)
        run_store.record("workflow", "guardrails", request.message, "blocked", total_ms, [blocked_step])
        return WorkflowResponse(
            answer=f"Request blocked by input guardrail: {input_verdict.reason}",
            agent="guardrails",
            route_reason="Input failed guardrail checks before reaching the supervisor",
            trace=[blocked_step],
            input_guardrail=input_verdict,
            output_guardrail=GuardrailVerdict(passed=True, rail="skipped", reason="Not evaluated (input blocked)"),
            total_latency_ms=total_ms,
        )

    guard_step = TraceStep(step="input_guardrail", agent="guardrails", detail=input_verdict.reason)

    # 2. Multi-agent graph execution.
    result = run_workflow(request.message, request.session_id)

    # 3. Output guardrails.
    answer, output_verdict = check_output(result.get("answer", ""))
    out_step = TraceStep(
        step="output_guardrail", agent="guardrails",
        detail=output_verdict.reason,
        status="ok" if output_verdict.passed else "blocked",
    )

    # 4. Persist chat history (writer agent uses it on future turns).
    if output_verdict.passed:
        history_store.append_exchange(request.session_id, request.message, answer)

    trace = [guard_step, *result.get("trace", []), out_step]
    total_ms = int((time.time() - start) * 1000)
    agent = result.get("route", "writer")
    run_store.record("workflow", agent, request.message, "ok" if output_verdict.passed else "blocked", total_ms, trace)

    return WorkflowResponse(
        answer=answer if output_verdict.passed else "Response blocked by output guardrail.",
        agent=agent,
        route_reason=result.get("route_reason", ""),
        sources=result.get("sources", []),
        trace=trace,
        input_guardrail=input_verdict,
        output_guardrail=output_verdict,
        total_latency_ms=total_ms,
    )
