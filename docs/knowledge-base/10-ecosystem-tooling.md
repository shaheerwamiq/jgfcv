# Ecosystem & Tooling

> Source: AI_compressed.pdf p. 1 (full tool list). This page maps every tool from the notes to its role, and what this project uses instead where applicable.

## Document processing
| Tool | Role | Notes |
| --- | --- | --- |
| **pypdf** | Pure-Python PDF text extraction | Used in this project for PDF uploads |
| **pymupdf** | Fast PDF parsing (C-based), better layout handling | Alternative when pypdf struggles |

## Vector stores & embeddings
| Tool | Role | Notes |
| --- | --- | --- |
| **chromadb** | Embedded vector DB with persistence | Alternative to FAISS (see KB 06) |
| **faiss-cpu** | In-process similarity search | Used here (in-memory) |
| **sentence-transformers** | Local embedding models (`all-MiniLM-L6-v2`) | Notes' choice; swapped for Gemini embeddings here (torch too heavy for serverless) |

## RAG variants & agents
| Tool | Role | Notes |
| --- | --- | --- |
| **pageindex.ai** | "Vectorless RAG" — hierarchical index the LLM navigates like a table of contents | Strong for long structured documents; no embedding drift |
| **deepagents** | Deep agents with planning, sub-agents, filesystem | Built on LangGraph |
| **tavily** | Web search API built for agents | The standard "search tool" for research agents |

## The LangChain family
| Tool | Role |
| --- | --- |
| **langchain** | Building blocks + chain-based agents |
| **langgraph** | Multi-agent workflows (state graphs) — used here |
| **langsmith** | LLM observability/tracing |
| **langchain adapters** | Bridge LangChain components to other frameworks |

## Pydantic family
| Tool | Role |
| --- | --- |
| **pydantic** | Validation — used by LangChain, CrewAI, AutoGen, FastAPI (and everywhere in this repo) |
| **pydantic-ai** | Agent framework built around typed outputs |
| **logfire** | Whole-application tracing (OpenTelemetry) |

## Safety & infrastructure
| Tool | Role | Notes |
| --- | --- | --- |
| **nemoguardrails** | Rails ("rules and regulations") in Colang | Concepts implemented as lightweight custom rails here (KB 08) |
| **guardrails (AI)** | Output validation framework | |
| **litellm** | LLM gateway: one API for all providers, cost tracking, fallbacks | |
| **Valkey** | Redis-fork datastore for caching/metrics | In-memory TTL cache stands in here (`core/cache.py`) |
| **fastmcp** | Build MCP (Model Context Protocol) servers in Python — expose tools to any MCP client | |
| **uv** | Fast Python package manager | Used by this project's backend |

## How to choose (rules of thumb)
- Start with the smallest thing that works: FAISS before Pinecone, custom rails before NeMo, logs before LangSmith.
- Prefer tools that compose (LCEL runnables, MCP tools) over monoliths.
- Every third-party service in the request path adds latency and a failure mode — count them.
