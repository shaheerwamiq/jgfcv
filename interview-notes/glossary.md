# Glossary of Key Terms

Quick-reference definitions for every term used in this project. Grouped by topic.

## LLM Fundamentals

- **LLM (Large Language Model):** A neural network trained on massive text corpora to predict the next token. Stateless between calls — all "memory" must be provided in the prompt.
- **Token:** The unit LLMs process (~0.75 words in English). Pricing and context limits are measured in tokens.
- **Context window:** Maximum number of tokens a model can attend to in one call (input + output).
- **Temperature:** Sampling randomness. 0 = near-deterministic, higher = more creative/varied.
- **System prompt:** Instructions that set the model's role and behavior, distinct from user messages.
- **Prompt injection:** An attack where user input tries to override the system prompt ("ignore previous instructions...").
- **Hallucination:** The model confidently generating false information. RAG and guardrails are the main mitigations.

## LangChain / LCEL

- **LangChain:** Framework providing abstractions (prompts, models, parsers, retrievers) for building LLM applications.
- **LCEL (LangChain Expression Language):** Composition syntax using `|` to pipe Runnables together: `prompt | llm | parser`.
- **Runnable:** Anything with `.invoke()` / `.stream()` / `.batch()` — the universal LangChain interface.
- **PromptTemplate / ChatPromptTemplate:** Templates with variables (`{topic}`) filled at invoke time; chat version produces role-tagged messages.
- **MessagesPlaceholder:** Slot in a chat prompt where a list of history messages is injected.
- **Output parser:** Transforms raw model output. `StrOutputParser` → plain string; `PydanticOutputParser` → validated Pydantic object.
- **RunnableLambda:** Wraps an arbitrary Python function as a Runnable so it can join a chain.
- **RunnableParallel:** Runs multiple chains concurrently on the same input, returning a dict of results.
- **RunnableBranch:** Routes input to one of several chains based on conditions (if/elif/else for chains).

## RAG

- **RAG (Retrieval-Augmented Generation):** Retrieve relevant documents for a query and pass them as context so the model answers from your data instead of its training data.
- **Document loader:** Reads a source (PDF, text, web page) into `Document` objects with `page_content` + `metadata`.
- **Chunking / text splitting:** Breaking documents into smaller overlapping pieces so they fit retrieval and context budgets. `RecursiveCharacterTextSplitter` is the standard.
- **Chunk overlap:** Shared characters between adjacent chunks so sentences aren't cut mid-thought at boundaries.
- **Embedding:** A vector of floats representing text meaning. Semantically similar texts have nearby vectors.
- **Cosine similarity:** Similarity metric between two vectors — the cosine of the angle between them (1 = identical direction).
- **Vector store:** Database optimized for storing embeddings and nearest-neighbor search (FAISS, Chroma, Pinecone, pgvector).
- **FAISS:** Facebook AI Similarity Search — fast, local, in-memory vector index. Great for dev/small scale.
- **Retriever:** LangChain interface that takes a query string and returns relevant `Document`s. `k` = number of results.
- **Grounding / citation:** Forcing the answer to be based on retrieved chunks and referencing which chunks were used.

## Agents & LangGraph

- **Agent:** An LLM that decides which actions/tools to take, observes results, and iterates until done.
- **Tool:** A function the agent can call (search, calculator, retriever) with a described interface.
- **LangGraph:** Library for building agent workflows as explicit state machines/graphs — nodes (steps) + edges (transitions), with shared state.
- **State (LangGraph):** Typed dict passed between nodes; each node reads it and returns updates.
- **Supervisor pattern:** A routing LLM node that examines the task and dispatches to specialist agents.
- **Conditional edge:** Graph edge whose target is chosen at runtime by a function of the state.
- **Multi-agent system:** Multiple specialized agents (research, analysis, writing) coordinated to solve a task no single prompt handles well.

## Production Concerns

- **Guardrail:** Programmatic check on LLM input or output (block injection, PII, unsafe content).
- **PII (Personally Identifiable Information):** Emails, phone numbers, SSNs — data that must not leak in outputs.
- **Observability / tracing:** Recording each step of a pipeline (inputs, outputs, latency, status) for debugging. LangSmith and Langfuse are the standard tools.
- **Exponential backoff:** Retry strategy where wait time doubles per attempt, usually with random jitter.
- **TTL cache:** Cache whose entries expire after a time-to-live, balancing freshness and cost savings.
- **Structured output:** Constraining model output to a schema (JSON/Pydantic) instead of free text.
- **Streaming:** Sending tokens to the client as they are generated rather than waiting for the full response.

## Stack-Specific

- **FastAPI:** Modern async Python web framework with automatic OpenAPI docs and Pydantic-based validation.
- **Pydantic:** Python data validation library. `BaseModel` classes validate and serialize data — used for API schemas AND LLM output parsing.
- **Gemini:** Google's LLM family. This project uses `gemini-2.0-flash` for generation and `text-embedding-004` for embeddings via `langchain-google-genai`.
- **uv:** Fast Python package manager used for the backend (`pyproject.toml`).
- **SWR:** React data-fetching library used by the frontend for caching and revalidation.
