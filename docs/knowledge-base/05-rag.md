# RAG — Retrieval Augmented Generation

> Source: Full_Stack.pdf pp. 7–9 ("Retrieve and Reason": `TextLoader`, `RecursiveCharacterTextSplitter`, FAISS, retrievers, `RetrievalQA`); AI_compressed.pdf p. 1 (pypdf, pymupdf, pageindex.ai vectorless RAG)

## What it is
RAG grounds LLM answers in your own documents. Pipeline: **Load → Split → Embed → Store → Retrieve → Generate.**
1. **Loader** reads raw documents (`TextLoader`; `pypdf`/`pymupdf` for PDFs).
2. **RecursiveCharacterTextSplitter** breaks "large text into small manageable chunks" while respecting paragraph/sentence boundaries.
3. Chunks are embedded and stored in a vector store (FAISS).
4. A **retriever** finds the top-k chunks for a query.
5. The LLM answers using retrieved chunks as "factual context of the answer" (`RetrievalQA` pattern).

## Why it exists
LLMs don't know your private data and hallucinate when asked. Fine-tuning is slow and expensive. RAG injects fresh, authoritative context at query time and enables citations.

## When to use it
- Question-answering over private/internal documents.
- Data that changes often (docs, tickets, policies).
- Anywhere answers must cite sources.

## When NOT to use it
- The answer is general world knowledge the model already has.
- The full document fits comfortably in the context window — just include it.
- Precise aggregations over structured data ("total Q3 revenue") — use SQL, not similarity search.

## Pros / Cons
| Pros | Cons |
| --- | --- |
| Grounded, citable answers | Quality ceiling = retrieval quality |
| Update knowledge by re-indexing, no retraining | Chunking choices materially affect results |
| Cheaper and faster than fine-tuning | More moving parts (loader, splitter, store, retriever) |

## Alternatives
- **Long-context stuffing** — for small corpora.
- **Fine-tuning** — teaches style/format, not facts; often combined with RAG.
- **Vectorless RAG (pageindex.ai, from the notes)** — hierarchical index navigated by the LLM like a table of contents; no embeddings, better for highly structured long documents.
- **Agentic RAG** — an agent decides when/what to retrieve, possibly multiple rounds (AgentForge's Research agent is a step in this direction).

## Common beginner mistakes
1. Chunks too large (retrieval imprecise) or too small (context fragmentary). Start ~1000 chars, overlap ~150.
2. No chunk overlap, cutting sentences in half at boundaries.
3. Retrieving top-k=1 — always fetch several chunks.
4. Not showing sources — users can't verify, trust collapses.
5. Evaluating by vibes instead of a fixed question set.

## Best practices
- Tune chunk size/overlap per corpus; log which chunks each answer used.
- Include chunk metadata (source, position) for citations.
- Tell the model to say "I don't know" when context is insufficient — and test that it does.

## In this project
- `backend/src/rag/loaders.py`, `splitter.py`, `vectorstore.py`, `pipeline.py` — the full pipeline.
- `/documents` page — upload, chunk, embed, index, then query with citations.
- Research agent (`backend/src/agents/research_agent.py`) — RAG as an agent capability.
