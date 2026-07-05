# Deployment & Local Development

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `GOOGLE_API_KEY` | Yes | Gemini chat + embedding calls (get one at https://aistudio.google.com) |
| `GEMINI_MODEL` | No | Chat model override (default `gemini-2.0-flash`) |
| `EMBEDDING_MODEL` | No | Embedding model override (default `models/text-embedding-004`) |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | No | RAG splitter tuning (defaults 1000 / 200) |

## Deploying on Vercel

The repo uses Vercel's multi-service configuration (`vercel.json`):

- `frontend/` — Next.js, serves the UI at `/`
- `backend/` — FastAPI, served under `/api/*` (prefix stripped before it reaches FastAPI)

Steps:
1. Push to GitHub and import the repo in Vercel (or use the Publish button in v0).
2. If you see a 404 after deploying, set **Settings → Build and Deployment → Framework Preset** to **Services**.
3. Add `GOOGLE_API_KEY` in Project Settings → Environment Variables.

### Serverless caveats

- FAISS index, run history, and chat memory are **in-memory** — they reset on cold starts and are not shared across instances. Fine for a demo/learning tool; see `docs/FUTURE_IMPROVEMENTS.md` for the production storage plan.
- Backend dependencies are kept lean (no torch) to stay under serverless size limits.

## Local Development

Prereqs: Node 20+, Python 3.11+, [uv](https://docs.astral.sh/uv).

```bash
# backend
cd backend
uv sync
GOOGLE_API_KEY=... uv run uvicorn main:app --reload --port 8000

# frontend (second terminal)
cd frontend
npm install
npm run dev   # http://localhost:3000
```

For local dev without Vercel's routing, either run `vercel dev` at the repo root, or add a rewrite in `frontend/next.config.ts` proxying `/api/*` to `http://localhost:8000/*`.

## Running Tests

```bash
cd backend
uv run pytest -q
```

Tests cover guardrails, retry/backoff, TTL cache, chat history windowing, text splitting, cosine similarity, and graph routing — all without hitting the Gemini API.
