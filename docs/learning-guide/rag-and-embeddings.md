# Learning Guide: Embeddings, Vector Stores & RAG

## Embeddings & similarity

**Level 1 — Beginner:** An embedding turns a sentence into a long list of numbers, like GPS coordinates for meaning. Sentences that mean similar things get nearby coordinates.

**Level 2 — Practical:** Call the embedding model on your texts, get vectors (e.g. 768 numbers each), compare with cosine similarity: closer to 1.0 = more similar. `all-MiniLM-L6-v2` runs locally via sentence-transformers; API models (Gemini, OpenAI) avoid shipping torch.

**Level 3 — Engineering:** Vectors from different models are incomparable — the model is part of your index schema. Long texts embed poorly (topics average out); embed chunks. Scores aren't calibrated probabilities; tune thresholds empirically per corpus.

**Level 4 — Senior:** Embedding choice is an architectural commitment: switching models means re-embedding everything. Design for it — store model ID with the index, make re-indexing a routine job. Consider hybrid retrieval (BM25 + vectors); lexical search still wins on exact terms, codes, and names.

**Level 5 — Interview:** "Embeddings map text into a vector space where semantic similarity becomes geometric proximity, measured by cosine similarity. Key production concerns: model consistency across index and query, chunk-level granularity, threshold calibration, and planned re-embedding when models change."

**Analogy:** Embeddings are a giant library where books are shelved by *what they're about*, not alphabetically. Two books on the same topic sit next to each other even if their titles share no words. Cosine similarity measures how many aisles apart two books live.

## Vector stores

**Level 1:** A vector store is a special filing cabinet that can instantly answer "which of my million notes is most similar to this one?"

**Level 2:** FAISS is a fast in-process index (in-memory; save/load manually). Chroma adds persistence and metadata filters. pgvector puts vectors in Postgres. Managed options (Pinecone, Qdrant) handle scale.

**Level 3:** Exact (flat) search is fine up to ~100k vectors; beyond that, ANN indexes (IVF, HNSW) trade a little recall for a lot of speed. Metadata filtering and multi-tenancy are where library-vs-database differences really bite.

**Level 4:** On serverless, in-memory indexes evaporate on cold start — either accept ephemerality (demo scope, like this project) or use a persistent external store. Treat index rebuilds as first-class operations with versioning and blue/green swaps.

**Level 5 — Interview:** "I pick the store by operational shape, not benchmarks: FAISS for in-process/ephemeral, Chroma for embedded persistence, pgvector when Postgres already exists, managed when scale or multi-tenancy demands. Flat index first, ANN only when latency data says so."

**Analogy:** FAISS is a brilliant filing system inside your own office — blazing fast, but if the office burns down (process restart), it's gone. A vector database is the bank vault across the street: slower to walk to, but fireproof.

## RAG

**Level 1:** RAG is giving the AI an open-book exam. Instead of answering from memory (and making things up), it first looks up the relevant pages from *your* documents, then answers using them.

**Level 2:** Pipeline: load (TextLoader/pypdf) → split (RecursiveCharacterTextSplitter, ~1000 chars, ~150 overlap) → embed → index (FAISS) → retrieve top-k → stuff into the prompt → generate with citations.

**Level 3:** Retrieval quality is the ceiling; generation can't fix bad context. Tune chunking to the corpus, retrieve k=3–5, include source metadata, and instruct the model to refuse when context is insufficient — then test that it does.

**Level 4:** Evaluate the two stages separately: retrieval (does the right chunk appear in top-k?) with a labeled question set, then generation (groundedness, citation accuracy). Most "RAG is bad" complaints are retrieval failures. Consider query rewriting, hybrid search, and re-ranking before touching the LLM. Know the variants: vectorless RAG (pageindex.ai-style hierarchical navigation) for long structured docs; agentic RAG when a single retrieval round isn't enough.

**Level 5 — Interview:** "RAG grounds generation in retrieved context: load, split, embed, store, retrieve, generate. My production checklist: chunking tuned per corpus, hybrid retrieval when exact terms matter, separate eval of retrieval vs generation, citations surfaced to users, and explicit 'insufficient context' behavior. Fine-tuning teaches style, RAG provides facts — they compose, they don't compete."

**Analogy:** An LLM alone is a professor answering from memory — eloquent, occasionally wrong, never cites. RAG hands the professor a folder of your documents and the instruction: "answer only from these pages, and give page numbers."
