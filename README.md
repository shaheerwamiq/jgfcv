# AgentForge — Multi-Agent AI Workflow Platform

A production-style multi-agent AI platform built with **LangChain, LangGraph, FastAPI, and Google Gemini**, paired with a Next.js console UI. It doubles as a complete learning repository: every concept from prompts and parsers to RAG, agents, guardrails, and observability is implemented in real code and documented in depth.

## What It Does

A **supervisor agent** (LangGraph) inspects each task and routes it through specialist agents:

- **Research Agent** — answers from your uploaded documents via a full RAG pipeline (loaders → recursive splitter → Gemini embeddings → FAISS → retriever) with citations.
- **Analyst Agent** — runs sequential + conditional LCEL chains producing Pydantic-validated structured analysis.
- **Writer Agent** — synthesizes prior agent output into the final response.

Every run is wrapped in **input/output guardrails** and recorded as a **step-by-step trace** you can inspect in the UI.

## UI

| Page | What it shows |
|---|---|
| `/` | Dashboard: system status, architecture, recent runs |
| `/workflow` | Run tasks through the agent graph, watch the trace |
| `/documents` | Upload/ingest docs, inspect chunks, RAG chat with citations |
| `/playground` | Chains demo, embedding similarity matrix, parser comparison |
| `/learn` | All project documentation rendered in-app |

## Concepts Covered (code ↔ docs)

| Concept | Code | Doc |
|---|---|---|
| Prompts & chat history | `backend/src/memory/` | `docs/knowledge-base/01` |
| Structured outputs & parsers | `backend/src/chains/parsers.py` | `docs/knowledge-base/02` |
| Sequential/conditional/parallel chains | `backend/src/chains/` | `docs/knowledge-base/03` |
| Embeddings & cosine similarity | `backend/src/llm/embeddings.py` | `docs/knowledge-base/04` |
| RAG pipeline | `backend/src/rag/` | `docs/knowledge-base/05` |
| Vector stores & retrievers | `backend/src/rag/vectorstore.py` | `docs/knowledge-base/06` |
| Agents & LangGraph | `backend/src/agents/` | `docs/knowledge-base/07` |
| Guardrails | `backend/src/guardrails/` | `docs/knowledge-base/08` |
| Observability & tracing | `backend/src/core/observability.py` | `docs/knowledge-base/09` |
| Retries, caching, config | `backend/src/core/` | `docs/knowledge-base/10` |

## Documentation

- `docs/ARCHITECTURE.md` — system design, request flow, module map, design decisions
- `docs/API.md` — full endpoint reference
- `docs/DEPLOYMENT.md` — Vercel + local dev setup
- `docs/LEARNING_GUIDE.md` + `docs/learning-guide/` — 5-level explanations (child → interview-ready)
- `docs/knowledge-base/` — 10 topic deep-dives
- `docs/FUTURE_IMPROVEMENTS.md` — honest gaps + production roadmap
- `cheatsheets/` — LCEL, RAG, LangGraph, Pydantic, FastAPI quick references
- `interview-notes/` — Q&A bank, best practices, glossary

## Quick Start

```bash
# 1. Set GOOGLE_API_KEY (https://aistudio.google.com)
# 2. Backend
cd backend && uv sync && GOOGLE_API_KEY=... uv run uvicorn main:app --port 8000
# 3. Frontend
cd frontend && npm install && npm run dev
```

Tests: `cd backend && uv run pytest -q` (39 tests, no API key needed).

## Stack

Python 3.11 · FastAPI · LangChain · LangGraph · FAISS · Google Gemini (`gemini-2.0-flash`, `text-embedding-004`) · Pydantic v2 · Next.js 15 · Tailwind CSS v4 · SWR — deployed as Vercel services (`vercel.json`).
