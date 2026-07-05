# Production Best Practices for LLM Applications

How AgentForge applies production engineering practices, and why each one matters. Use these as talking points when explaining the project.

## 1. Structured Outputs Everywhere

**Practice:** Never parse LLM free text with string manipulation. Use Pydantic schemas via `PydanticOutputParser` (see `backend/src/chains/parsers.py`).

**Why:** LLM output is non-deterministic. A schema gives you a contract: if the model returns malformed JSON, you fail fast with a clear error instead of silently propagating garbage. In AgentForge, the supervisor's routing decision and the analyst's report are both schema-validated.

## 2. Guardrails on Both Sides

**Practice:** Validate input BEFORE it reaches the LLM (`guardrails/input_rails.py`) and output BEFORE it reaches the user (`guardrails/output_rails.py`).

**Why:** Input rails block prompt injection, off-topic abuse, and oversized payloads (cost control). Output rails catch leaked system prompts, PII, and unsafe content. Defense in depth — never trust either side of the model.

## 3. Retries with Exponential Backoff

**Practice:** All LLM calls go through `with_retry()` (`core/retry.py`) — exponential backoff with jitter, capped attempts.

**Why:** LLM APIs fail transiently (429 rate limits, 5xx). Naive immediate retries amplify load spikes; jittered backoff spreads them out. Capped attempts prevent infinite loops and runaway cost.

## 4. Caching

**Practice:** TTL cache on embeddings and repeated LLM calls (`core/cache.py`), keyed by a hash of the input.

**Why:** Embedding the same text twice is pure waste. In RAG, popular queries repeat often. Caching cuts both latency and API spend. TTL keeps results from going permanently stale.

## 5. Observability / Tracing

**Practice:** Every workflow run records a trace: each agent step with inputs, outputs, timing, and status (`core/observability.py`). Exposed via `/api/workflows/runs`.

**Why:** Multi-agent systems are opaque — when output is wrong you need to know WHICH step failed and what it saw. This mirrors what LangSmith/Langfuse do in production; the in-repo version keeps the demo self-contained.

## 6. Fail Fast, Fail Loud

**Practice:** Custom exception hierarchy (`core/errors.py`) mapped to proper HTTP status codes in one FastAPI exception handler.

**Why:** Distinguishing `GuardrailViolation` (400, user's fault) from `LLMError` (502, upstream fault) from `NotFoundError` (404) makes debugging and client handling straightforward. Never swallow exceptions into generic 500s.

## 7. Config from Environment

**Practice:** All settings (model names, chunk sizes, retry counts) live in `core/config.py` and read from environment variables with sensible defaults.

**Why:** Twelve-factor apps. You can change the model or chunk size in deployment without a code change. Secrets (`GOOGLE_API_KEY`) never live in code.

## 8. Session-Scoped Chat History

**Practice:** Conversation memory keyed by session ID with a max-turns window (`memory/chat_history.py`).

**Why:** LLMs are stateless — history must be replayed each call. Windowing caps token cost and prevents context overflow. Session scoping prevents users' conversations from leaking into each other.

## 9. Testing Without the LLM

**Practice:** Unit tests cover guardrails, cache, retry, splitter, cosine similarity, and graph routing logic with the LLM mocked or bypassed (`backend/tests/`).

**Why:** Deterministic logic should be tested deterministically. Hitting a real LLM in unit tests is slow, flaky, and costs money. The seams (dependency injection of the LLM client) are designed for this.

## 10. Cost Discipline

**Practice:** Input length limits, retrieval k-limits, windowed memory, caching, and a cheap-model-first policy (Gemini Flash).

**Why:** Token cost scales linearly with context. Most production LLM bills are dominated by unnecessarily long prompts. Every context token should earn its place.
