# API Reference

All endpoints are served under `/api/*` (Vercel strips the prefix before forwarding to FastAPI). Interactive OpenAPI docs are available at `/api/docs` when running locally.

## System

### `GET /api/health`
Returns service status and whether `GOOGLE_API_KEY` is configured.

```json
{ "status": "ok", "llm_configured": true, "model": "gemini-2.0-flash" }
```

### `GET /api/stats`
Counts of ingested documents, chunks, total workflow runs, and cache stats.

## Workflows

### `POST /api/workflows/run`
Run the multi-agent workflow on a task.

Request:
```json
{ "task": "Research the benefits of RAG and write a summary", "session_id": "optional-session" }
```

Response:
```json
{
  "run_id": "run_ab12cd34",
  "answer": "…final synthesized answer…",
  "route": "research",
  "trace": [
    { "step": "input_guardrails", "status": "passed", "duration_ms": 1 },
    { "step": "supervisor", "status": "completed", "detail": "route=research", "duration_ms": 640 },
    { "step": "research_agent", "status": "completed", "duration_ms": 1210 },
    { "step": "writer_agent", "status": "completed", "duration_ms": 980 },
    { "step": "output_guardrails", "status": "passed", "duration_ms": 2 }
  ]
}
```

Errors: `400` guardrail violation (body includes the reason), `502` LLM failure after retries.

### `GET /api/workflows/runs`
List recent runs (id, task, route, status, timestamps).

### `GET /api/workflows/runs/{run_id}`
Full trace for one run.

## Documents (RAG)

### `POST /api/documents/upload`
Multipart upload (`file`): PDF, `.txt`, or `.md`. Loads, splits, embeds, and indexes the document.

Response: `{ "document_id": "...", "filename": "...", "chunks": 12 }`

### `POST /api/documents/ingest-text`
Ingest raw text without a file: `{ "text": "...", "title": "My Notes" }`.

### `GET /api/documents`
List ingested documents with chunk counts.

### `GET /api/documents/{doc_id}/chunks`
Inspect the actual chunks (content + metadata) a document was split into.

### `POST /api/documents/query`
RAG query: `{ "question": "...", "k": 4, "session_id": "optional" }`.

Response includes the grounded `answer` and the `sources` (chunk content, document, similarity score) used.

### `DELETE /api/documents/{doc_id}`
Remove a document and its chunks from the index.

## Playground

### `POST /api/playground/chain`
Run a demo chain. `{ "chain_type": "sequential" | "conditional" | "parallel", "input": "..." }`. Response includes each intermediate step's output.

### `POST /api/playground/embed`
Compare texts: `{ "texts": ["a", "b", "c"] }` → pairwise cosine similarity matrix plus embedding dimension.

### `POST /api/playground/parse`
Same prompt run through `StrOutputParser` vs `PydanticOutputParser`: `{ "text": "..." }` → both raw string and validated JSON object, side by side.
