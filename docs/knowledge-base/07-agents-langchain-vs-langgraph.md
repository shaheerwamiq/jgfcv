# Agents: LangChain vs LangGraph (vs LangSmith)

> Source: AI_compressed.pdf p. 1 ("langchain — chain based agents; langgraph — multi agentic workflows; langsmith — observability; deepagents")

## What it is
- **LangChain** — building blocks (prompts, chains, tools, retrievers) and *chain-based agents*: linear or branching pipelines.
- **LangGraph** — *multi-agent workflows* modeled as a state graph: nodes are agents/functions, edges (including conditional edges) define routing, and a shared typed state flows through. Supports cycles, checkpoints, and human-in-the-loop.
- **LangSmith** — the observability layer (tracing every step); covered in `09-observability.md`.
- **deepagents** (from the notes) — a library for "deep" agents with planning, sub-agents, and file-system access, built on LangGraph.

## Why it exists
Chains are DAGs: they cannot loop, retry with modified state, or let one agent decide to call another. Multi-agent systems need routing decisions made *at runtime* by an LLM — that requires a graph with conditional edges and shared state.

## When to use which
| Situation | Use |
| --- | --- |
| Fixed steps, known order | LCEL chain |
| One-off branch on input type | `RunnableBranch` |
| Runtime routing between specialists | LangGraph supervisor |
| Loops (draft → critique → redraft) | LangGraph |
| Long-running, resumable, human approval | LangGraph + checkpoints |

## When NOT to use LangGraph
- A single prompt or fixed pipeline — a graph adds ceremony without value.
- Hard-real-time paths where an extra LLM routing call is unacceptable.

## Supervisor pattern (used here)
A supervisor node classifies the request and routes to a specialist:
- **Research agent** — retrieves from the document index (RAG) and answers with citations.
- **Analyst agent** — runs parallel structured analysis (summary, sentiment, key points) with Pydantic-validated output.
- **Writer agent** — composes/rewrites prose.
Guardrails run before (input rails) and after (output rails) the graph. Every node appends a trace step to state.

## Pros / Cons
| Pros | Cons |
| --- | --- |
| Runtime routing, cycles, shared state | More components to test |
| Each agent stays small and focused | Routing LLM call adds latency + cost |
| Trace of every hop for observability | Poor routing prompt = wrong specialist |

## Common beginner mistakes
1. Making every agent a giant prompt instead of one job each.
2. Unbounded loops — always cap iterations in graph state.
3. Passing entire conversation state to every node (token waste).
4. No trace — multi-agent systems are undebuggable without step logs.

## Best practices
- Give the supervisor an explicit, short list of routes with one-line criteria.
- Type the graph state (`TypedDict`) and keep it minimal.
- Record agent, action, latency per node (see `core/observability.py`).

## In this project
- `backend/src/agents/state.py` — typed shared state.
- `backend/src/agents/supervisor.py` — structured-output router.
- `backend/src/agents/graph.py` — `StateGraph` wiring with conditional edges.
