# Embeddings & Cosine Similarity

> Source: Full_Stack.pdf pp. 6–7 (`HuggingFaceEmbeddings`, `all-MiniLM-L6-v2`, `sklearn cosine_similarity`); AI_compressed.pdf p. 1 (`sentence-transformers`)

## What it is
An embedding maps text to a dense vector such that semantically similar texts land close together. Cosine similarity measures the angle between two vectors: 1.0 = identical direction, 0 = unrelated. The course notes use HuggingFace `sentence-transformers` with `all-MiniLM-L6-v2` (384 dimensions, runs locally) and scikit-learn's `cosine_similarity`.

## Why it exists
Keyword search misses meaning ("reset password" vs. "can't log in"). Embeddings enable semantic search, clustering, deduplication, recommendation — and are the foundation of RAG retrieval.

## When to use it
- Semantic search / RAG retrieval.
- Finding duplicates or near-duplicates.
- Routing by semantic similarity to exemplar phrases.

## When NOT to use it
- Exact-match lookups (IDs, SKUs) — use a normal index.
- Tiny corpora (< 50 short items) where an LLM can just read everything.
- Cross-lingual or domain-heavy text with a general-purpose model — pick a specialized model.

## Pros / Cons
| Pros | Cons |
| --- | --- |
| Captures meaning, not keywords | Model choice locks your index (re-embed to switch) |
| Fast approximate search at scale | Embeddings of long texts blur multiple topics |
| Cheap compared to LLM calls | Similarity scores are relative, not calibrated probabilities |

## Alternatives
- **Local sentence-transformers** (course notes' choice) — free, private, but needs torch (~2 GB), unsuitable for serverless.
- **API embeddings** (Gemini `embedding-001`, OpenAI `text-embedding-3-*`) — no local model weight, per-call cost. **AgentForge uses Gemini embeddings for this reason** — documented trade-off.
- **BM25 / keyword search** — still excellent; hybrid (BM25 + vectors) often beats either alone.

## Common beginner mistakes
1. Comparing vectors from different embedding models.
2. Embedding entire documents instead of chunks (meaning gets averaged away).
3. Using Euclidean distance on non-normalized vectors when cosine was intended.
4. Assuming a score of 0.8 "means" 80% similar — thresholds must be tuned per model/corpus.

## Best practices
- Normalize and batch embedding calls; cache repeated inputs (see `core/cache.py`).
- Keep the embedding model identifier stored alongside the index.
- Evaluate retrieval quality with a small labeled set before trusting thresholds.

## In this project
- `backend/src/llm/embeddings.py` — Gemini embeddings + pure-Python cosine similarity (mirrors the sklearn approach from the notes without the dependency).
- Playground → "Embedding Similarity" tab ranks candidate sentences against a query, live.
