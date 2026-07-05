# Future Improvements

Honest gaps in the current implementation and how each would be addressed in a production system. Useful interview material: knowing what your system does NOT do is as important as what it does.

## Storage & State

- **Persistent vector store.** FAISS is in-memory and per-instance. Swap to pgvector (Postgres) or Pinecone so the index survives restarts and is shared across serverless instances. The `VectorStoreManager` interface in `rag/vectorstore.py` is the seam for this swap.
- **Persistent run history.** The observability store is an in-memory dict. Move to Postgres (or ship traces to LangSmith/Langfuse) for durable, queryable run history.
- **Durable chat memory.** Session history should live in Redis (with TTL) or Postgres instead of process memory.

## Model Layer

- **Streaming responses.** Stream tokens over SSE from FastAPI and render incrementally in the UI — better perceived latency for long writer-agent outputs.
- **Model fallbacks.** On repeated Gemini failures, fall back to a second provider via a model-router abstraction.
- **Semantic caching.** Current cache is exact-match on input hash. A semantic cache (embed the query, serve cached answers above a similarity threshold) would raise hit rates substantially.

## RAG Quality

- **Reranking.** Add a cross-encoder or LLM reranker over the top-k retrieved chunks before generation.
- **Hybrid search.** Combine dense (embedding) retrieval with BM25 keyword retrieval; fuse with reciprocal rank fusion.
- **Query rewriting.** Rewrite conversational queries ("what about the second one?") into standalone queries using chat history before retrieval.
- **Evaluation harness.** Add a golden-answer dataset and automated RAG evals (faithfulness, answer relevance, context precision — RAGAS-style).

## Agents

- **Tool-calling agents.** Current agents are fixed pipelines around LLM calls. Add real tools (web search, calculator, code execution) with LangGraph's ToolNode.
- **Human-in-the-loop.** LangGraph interrupts to pause the graph for user approval before expensive or irreversible steps.
- **Parallel agent execution.** Research and analysis paths could fan out concurrently and join at the writer.
- **Checkpointing.** LangGraph checkpointers would let long runs resume after failures.

## Guardrails & Security

- **ML-based moderation.** Replace regex/keyword rails with a moderation model or service for robustness against paraphrased attacks.
- **Rate limiting.** Per-session/IP limits (e.g., Upstash Redis) to control cost abuse.
- **AuthN/AuthZ.** Add user accounts so documents and run history are scoped per user.

## Frontend

- **Live trace streaming.** Currently the trace arrives with the final response; SSE would show each agent step as it happens.
- **Graph visualization.** Render the LangGraph topology and highlight the active path per run.
