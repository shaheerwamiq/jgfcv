# Interview Questions & Senior-Level Answers

Grouped by topic. Answers are written the way a senior engineer would actually say them.

## LangChain & Chains

**Q: What is LCEL and why does it exist?**
A: LangChain Expression Language — declarative composition of Runnables with the pipe operator. Every component (prompt, model, parser, function) shares one interface, so composing them yields a pipeline that gets streaming, batching, async, and tracing for free. It exists to replace brittle imperative glue code between LLM steps.

**Q: Sequential vs parallel vs conditional chains — when do you use each?**
A: Sequential when step N needs step N-1's output (outline → draft). Parallel (`RunnableParallel`) when branches are independent over the same input — it cuts wall-clock latency to the slowest branch instead of the sum. Conditional (`RunnableBranch`) when input type determines handling. If routing must happen repeatedly at runtime or the flow needs cycles, none of these — that's LangGraph.

**Q: What does `StrOutputParser` actually do and why is it everywhere?**
A: It extracts the string content from a model's message object. It matters because chain steps expect strings; without it the next prompt template receives an `AIMessage` and either errors or interpolates garbage. It's the standard glue between steps in multi-step workflows.

**Q: How do you get reliable structured output from an LLM?**
A: Preference order: provider-native structured output (`with_structured_output` / JSON mode) constrained by a Pydantic schema; then `PydanticOutputParser` with format instructions in the prompt; regex only as a last resort. In all cases: flat schemas, described fields, and a retry loop that feeds validation errors back to the model once. Measure parse-rate in production.

## Embeddings & RAG

**Q: Explain embeddings to a non-ML engineer.**
A: A function that maps text to a point in high-dimensional space such that semantic similarity becomes geometric proximity. "Reset my password" and "can't log in" land close together despite sharing no keywords. Compare points with cosine similarity; that powers semantic search, dedup, and RAG retrieval.

**Q: Walk me through a production RAG pipeline.**
A: Ingest: load (pypdf/TextLoader), split with RecursiveCharacterTextSplitter (~1000 chars, ~150 overlap, tuned per corpus), embed each chunk, index in a vector store with source metadata. Query: embed the question, retrieve top-k (3–5), optionally re-rank, build a grounded prompt that demands citations and permits "I don't know", generate, and log the whole trace. Evaluate retrieval and generation separately — retrieval quality is the ceiling.

**Q: Why chunk documents at all? What goes wrong with bad chunking?**
A: Embedding a whole document averages its topics into mush — retrieval becomes imprecise. Too-small chunks lose surrounding context. No overlap slices sentences at boundaries. Chunking is the highest-leverage RAG tuning knob and the first thing I inspect when quality is poor.

**Q: RAG vs fine-tuning?**
A: Different jobs. RAG injects *facts* at query time — updatable by re-indexing, citable, cheap. Fine-tuning teaches *style, format, and task behavior* — it does not reliably add facts and goes stale. They compose: fine-tune for the domain voice, RAG for the knowledge.

**Q: When would you NOT use a vector database?**
A: Corpus small enough to stuff in context; exact-match lookups (use a normal index); precise aggregations over structured data (use SQL); or when Postgres+pgvector already exists and a new component isn't justified.

**Q: FAISS vs Chroma vs pgvector?**
A: Operational shape, not benchmarks. FAISS: in-process library, fastest, manual persistence — prototypes and ephemeral indexes. Chroma: embedded DB, persistence and metadata filters built in. pgvector: vectors inside existing Postgres — transactions and one less system. Managed (Pinecone/Qdrant/Weaviate) when scale or multi-tenancy demands it.

## Agents & LangGraph

**Q: LangChain vs LangGraph vs LangSmith?**
A: LangChain = building blocks and chain-based agents (DAGs). LangGraph = multi-agent workflows as state machines — typed shared state, nodes, conditional edges, cycles, checkpoints. LangSmith = observability/tracing and evals. Rule of thumb: fixed pipeline → chain; runtime routing, loops, or agent handoffs → graph; debugging either → LangSmith.

**Q: Design a multi-agent system for [X]. How do you structure it?**
A: Supervisor pattern: a router node classifies the request via structured output (an enum of routes — never parsed free text) and conditionally routes to single-responsibility specialists. Shared typed state, append-only trace, iteration caps on any cycle, guardrails outside the graph boundary, and per-node latency/token recording. Exactly the shape of this project's `agents/graph.py`.

**Q: What failure modes do agents have that chains don't?**
A: Unbounded loops (cost explosions), wrong-tool selection, confident wrong-path execution, and state bloat. Mitigations: capped iterations, small action spaces, structured routing decisions, and full step tracing so failures are reconstructable.

## Guardrails & Security

**Q: How do you defend against prompt injection?**
A: Defense in depth — the system prompt is not a security boundary. Input rails: pattern checks for known injection phrasings, then an LLM classifier for paraphrases. Output rails: PII regexes, policy screen, grounding check against retrieved context. Also treat the RAG corpus as an attack surface (indirect injection via documents). Fail closed on high-risk actions, log every verdict, and keep an attack regression suite.

**Q: What is NeMo Guardrails / Colang?**
A: NVIDIA's rails framework — rails are rules governing what enters and leaves the model, defined in Colang, a dialogue-flow DSL. Powerful for conversational policies; heavyweight as a dependency. For most services, layered lightweight rails (regex → LLM check → output screen) cover the need — which is what this repo implements.

## Observability & Production

**Q: What do you log for an LLM application?**
A: Per run: run ID, input hash, every step (agent, action, prompt/response or a redacted digest, latency, token estimate), guardrail verdicts, model + parameters, and final status. Correlate across services with the run ID. Cost tracking is part of observability — tokens are money.

**Q: LangSmith vs Logfire?**
A: LangSmith traces the LLM layer — chain/agent call trees, prompt diffs, evals. Logfire (Pydantic) traces the whole application over OpenTelemetry — HTTP, DB, and LLM in one timeline. Complementary; small teams can start with structured logs + run IDs and adopt either later.

**Q: How do you keep latency acceptable in an LLM API?**
A: Parallelize independent LLM calls (`RunnableParallel`), stream tokens to the user, cache embeddings and repeated completions (TTL cache here; Redis/Valkey at scale), use fast models for routing/classification and big models only where quality demands, set timeouts with retries and jitter, and measure per-step latency so you optimize the actual bottleneck.

## Pydantic & FastAPI

**Q: Why is Pydantic so central to the Python AI stack?**
A: It's the shared validation contract: FastAPI uses it for request/response schemas, LangChain for structured outputs and tool schemas, agent frameworks (CrewAI, AutoGen, pydantic-ai) for typed agent I/O. One schema serves as API contract, LLM output constraint, documentation, and test fixture.

**Q: Sync vs async in FastAPI for LLM calls?**
A: LLM calls are slow I/O — use async clients inside `async def` so the event loop can serve other requests during the wait. A sync SDK call inside `async def` blocks the loop for everyone; if a lib is sync-only, use a plain `def` endpoint (threadpool) or an executor.
