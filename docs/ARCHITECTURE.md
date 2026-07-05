# Architecture

AgentForge is a two-service application: a Python FastAPI backend implementing the AI systems, and a Next.js frontend for interacting with them. Vercel's services routing sends `/api/*` to the backend and everything else to the frontend.

## System Overview

```
┌────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                   │
│  Dashboard │ Workflow Runner │ Documents │ Playground │ Learn│
└──────────────────────────┬─────────────────────────────────┘
                           │  /api/* (Vercel routes, prefix stripped)
┌──────────────────────────▼─────────────────────────────────┐
│                       Backend (FastAPI)                     │
│                                                             │
│  api/workflows ── api/documents ── api/playground ── system │
│        │                │                │                  │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌────▼─────┐            │
│  │ LangGraph │    │    RAG    │    │  Chains  │            │
│  │ supervisor│    │ loaders → │    │ seq/cond/│            │
│  │ → agents  │    │ splitter →│    │ parallel │            │
│  └─────┬─────┘    │ FAISS →   │    └────┬─────┘            │
│        │          │ retriever │         │                  │
│        │          └─────┬─────┘         │                  │
│  ┌─────▼────────────────▼───────────────▼─────┐            │
│  │  Cross-cutting: guardrails · retry · cache  │            │
│  │  · observability · chat history · config    │            │
│  └─────────────────────┬───────────────────────┘            │
│                        │                                    │
│              Google Gemini API                              │
│     (gemini-2.0-flash + text-embedding-004)                 │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow: Workflow Run

1. `POST /api/workflows/run` with `{task, session_id}`.
2. **Input guardrails** validate the task (length, injection patterns, blocklist). Violations → 400 before any LLM spend.
3. A **run record** is created in the observability store; every subsequent step appends a trace entry.
4. The **supervisor** node (structured-output LLM call) classifies the task and picks an agent route.
5. The chosen path executes:
   - **Research agent** — retrieves from FAISS (if documents ingested), answers with citations.
   - **Analyst agent** — sequential + conditional chains producing a Pydantic-validated analysis.
   - **Writer agent** — takes prior agent output (or raw task) and produces the final formatted response.
6. **Output guardrails** scan the final text (PII, system-prompt leakage).
7. The full trace (steps, timings, statuses) returns with the answer and is queryable at `GET /api/workflows/runs/{id}`.

## Module Map (backend/src)

| Module | Responsibility | Key concepts demonstrated |
|---|---|---|
| `core/config.py` | Env-driven settings | 12-factor config |
| `core/errors.py` | Exception hierarchy → HTTP codes | Fail fast, typed errors |
| `core/retry.py` | Exponential backoff + jitter | Resilient LLM calls |
| `core/cache.py` | TTL cache | Cost/latency optimization |
| `core/observability.py` | Run/trace store | Tracing, debugging multi-agent runs |
| `llm/client.py` | Gemini chat model factory | Model abstraction |
| `llm/embeddings.py` | Embeddings + cosine similarity | Vector math |
| `chains/parsers.py` | Str/Pydantic output parsers | Structured outputs |
| `chains/sequential.py` | Multi-step LCEL pipe | Sequential chains |
| `chains/conditional.py` | RunnableBranch routing | Conditional chains |
| `chains/parallel.py` | RunnableParallel fan-out | Parallel chains |
| `rag/loaders.py` | PDF/text/markdown loading | Document loaders |
| `rag/splitter.py` | Recursive chunking | Chunk size/overlap trade-offs |
| `rag/vectorstore.py` | FAISS index + retriever | Vector stores, retrievers |
| `rag/pipeline.py` | Ingest → retrieve → answer | End-to-end RAG |
| `agents/state.py` | Graph state TypedDict | Shared agent state |
| `agents/supervisor.py` | Routing node | Supervisor pattern |
| `agents/research_agent.py` | RAG-backed agent | Retrieval agents |
| `agents/analyst_agent.py` | Chain-backed agent | Chains inside agents |
| `agents/writer_agent.py` | Synthesis agent | Composition |
| `agents/graph.py` | StateGraph wiring | LangGraph, conditional edges |
| `guardrails/input_rails.py` | Pre-LLM validation | Injection defense |
| `guardrails/output_rails.py` | Post-LLM scanning | PII/leak defense |
| `memory/chat_history.py` | Windowed session memory | Chat history |
| `schemas/models.py` | API request/response models | Pydantic contracts |

## Key Design Decisions

- **In-memory FAISS + run store:** self-contained demo with zero external infra. Trade-off: state resets on cold start. Production swap: pgvector/Pinecone + Postgres (documented in `docs/FUTURE_IMPROVEMENTS.md`).
- **Gemini embeddings instead of sentence-transformers:** torch is too heavy for serverless; API embeddings keep the deploy small. The concept (embed → store → search) is identical.
- **Custom guardrails instead of nemoguardrails:** the library needs its own model configs and heavier deps; the custom rails make the underlying checks explicit and testable — better for learning.
- **Supervisor over router-less agents:** an explicit routing node with a structured output makes the decision inspectable in the trace.

## Frontend Structure

- `app/page.tsx` — dashboard (system status, architecture summary, recent runs)
- `app/workflow/` — task input, agent path visualization, live trace, result
- `app/documents/` — upload/ingest, chunk inspection, RAG chat with citations
- `app/playground/` — chains demo, embedding similarity, parser comparison
- `app/learn/` — renders the markdown docs from `docs/`, `cheatsheets/`, `interview-notes/`
- `lib/api.ts` — typed fetchers used with SWR
- Data flow: SWR for reads, plain fetch for actions; no client state library needed.
