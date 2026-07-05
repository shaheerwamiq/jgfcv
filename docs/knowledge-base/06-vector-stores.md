# Vector Stores (FAISS, Chroma & Friends)

> Source: Full_Stack.pdf p. 8 ("FAISS — Facebook AI Similarity Search — store and search document", FAISS index); AI_compressed.pdf p. 1 (`chromadb`, `faiss-cpu`)

## What it is
A vector store indexes embedding vectors for fast nearest-neighbor search. **FAISS** (Facebook AI Similarity Search) is an in-process library — the "FAISS index" lives in memory (optionally saved to disk). **ChromaDB** is an embeddable vector database with persistence and metadata filtering built in.

## Why it exists
Brute-force cosine similarity over millions of vectors is too slow. Vector stores use ANN (approximate nearest neighbor) index structures to answer top-k queries in milliseconds.

## When to use it
- Any RAG system beyond a handful of documents.
- Semantic caching, deduplication, recommendations at scale.

## When NOT to use it
- Tiny corpora — a Python list + cosine loop is simpler and exact.
- When you already run Postgres — `pgvector` avoids a new component.
- Exact keyword/ID lookups.

## Choosing a store
| Store | Type | Persistence | Best for |
| --- | --- | --- | --- |
| FAISS | in-process library | manual (save/load) | prototypes, ephemeral indexes, this project |
| ChromaDB | embedded DB | built-in | local apps needing persistence + metadata filters |
| pgvector | Postgres extension | full DB | teams already on Postgres |
| Pinecone/Weaviate/Qdrant | managed/served | full | production scale, multi-tenant |

## Pros / Cons (FAISS specifically)
| Pros | Cons |
| --- | --- |
| Extremely fast, battle-tested | No built-in persistence/server — you manage it |
| Zero infrastructure | Index lost on process restart (relevant on serverless!) |
| Many index types (flat, IVF, HNSW) | No metadata filtering out of the box |

## Common beginner mistakes
1. Expecting an in-memory FAISS index to survive serverless cold starts — it will not. AgentForge documents this: uploaded documents live for the lifetime of the backend instance; production should use a persistent store.
2. Using approximate indexes for tiny datasets (adds error, saves nothing).
3. Storing raw text only in the vector store with no source metadata.
4. Never rebuilding the index after changing embedding models.

## Best practices
- Persist alongside the embedding model name and chunking parameters.
- Start with a flat (exact) index; switch to ANN only when latency demands it.
- Plan re-indexing as a routine operation, not an emergency.

## In this project
- `backend/src/rag/vectorstore.py` — FAISS via `langchain_community`, in-memory, with a documented persistence trade-off and singleton access.
