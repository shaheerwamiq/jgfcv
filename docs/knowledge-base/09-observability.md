# Observability & Tracing

> Source: AI_compressed.pdf p. 1 ("pydantic logfire — trace entire application; langsmith is for tracing LLM observability"; "Betterdb with Valkey — Observability"; "litellm.ai — gateway")

## What it is
Observability for LLM apps means capturing every step of every run: which agents ran, what prompts were sent, latency, token usage, guardrail verdicts, and errors.

- **LangSmith** — LLM-specific tracing: every chain/agent/LLM call as a nested trace tree, with prompt/response capture and eval tooling.
- **Pydantic Logfire** — traces the *entire application* (FastAPI requests, DB calls, LLM calls) on OpenTelemetry; broader than LangSmith.
- **LiteLLM** — a gateway in front of many LLM providers: one API, plus centralized logging, cost tracking, rate limits, fallbacks.
- **Valkey** (Redis fork, from the notes) — backing store for metrics/counters/queues in observability pipelines.

## Why it exists
LLM systems fail silently: a bad retrieval, a mis-route, a truncated prompt. Without traces you debug by guessing. Cost also scales with tokens — untracked spend surprises teams.

## When to use what
| Need | Tool |
| --- | --- |
| Debug chains/agents, compare prompts | LangSmith |
| Whole-app performance (API + LLM) | Logfire / OpenTelemetry |
| Multi-provider routing, cost caps | LiteLLM gateway |
| Lightweight, zero-dependency traces | Structured logs + in-app trace (this project) |

## When NOT to add heavy tooling
- Prototypes — structured logging is enough to start (but add request IDs from day one).
- Never send prompt/response bodies containing user PII to third-party trace services without review.

## Pros / Cons of managed tracing
| Pros | Cons |
| --- | --- |
| Zero-effort deep traces | Data leaves your infrastructure |
| Eval/regression tooling included | Per-trace pricing at scale |
| Team-shareable debugging | Vendor coupling |

## Common beginner mistakes
1. Logging only errors — successful-but-wrong runs are the hard bugs.
2. No correlation ID across steps of one request.
3. Measuring latency without token counts (cost blindness).
4. Leaving verbose prompt logging on in production (PII + volume).

## Best practices
- Attach a run ID to every workflow; record per-step agent, action, latency.
- Estimate tokens per step; surface totals in the UI.
- Keep traces queryable (in-memory ring buffer here; a DB or LangSmith in production).

## In this project
- `backend/src/core/observability.py` — run store: every workflow run keeps a full step trace.
- `backend/src/core/logging.py` — structured JSON logs with run IDs.
- `/workflow` page — renders the live trace: agents, guardrail verdicts, latency per step.
- `GET /api/observability/runs` — recent runs for the dashboard.
