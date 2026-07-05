# Chains & LCEL (Sequential, Conditional, Parallel)

> Source: Full_Stack.pdf pp. 3–6 (chains, `prompt1 | model | prompt2 | model | parser`, `RunnableBranch`, `RunnableLambda`, `RunnableParallel`)

## What it is
LCEL (LangChain Expression Language) composes components with the `|` pipe operator. Every component is a `Runnable` with a uniform interface (`invoke`, `stream`, `batch`).

- **Sequential chain** — "step by step … multiple models into one workflow": `prompt1 | model | parser | prompt2 | model | parser`. Output of one step is input to the next.
- **Conditional chain** — `RunnableBranch` routes to different sub-chains based on a predicate; `RunnableLambda` wraps arbitrary Python functions as chain steps.
- **Parallel chain** — `RunnableParallel` runs independent branches concurrently: "save time, efficient, many tasks".

## Why it exists
Real tasks need multiple LLM calls (outline → draft → critique). LCEL gives a declarative composition model with built-in streaming, batching, retries, and async — instead of hand-written glue code.

## When to use it
- Sequential: any multi-step reasoning where step N depends on step N-1.
- Conditional: different handling per input type (complaint vs. praise, question vs. command).
- Parallel: independent sub-tasks over the same input (summary + keywords + sentiment).

## When NOT to use it
- One prompt, one answer — a single `prompt | llm | parser` is all you need; don't add steps.
- Loops, retries-with-state, or multi-agent handoffs — that's a graph problem; use LangGraph.
- Branching that depends on runtime tool results — LCEL branches are chosen once; graphs re-route dynamically.

## Pros / Cons
| Pros | Cons |
| --- | --- |
| Declarative, readable pipelines | Sequential latency adds up per step |
| Free streaming/batch/async on the whole chain | Debugging mid-chain state requires tracing |
| Parallel branches cut wall-clock time | No cycles — DAG only |

## Alternatives
- **Plain Python functions** calling the LLM — more control, no free streaming/tracing.
- **LangGraph** — when you need cycles, state, or agent routing.

## Common beginner mistakes
1. Forgetting `StrOutputParser()` between steps, so the next prompt receives a `AIMessage` object instead of a string.
2. Using sequential chains for independent tasks (3x slower than `RunnableParallel`).
3. Making every step an LLM call when a `RunnableLambda` (plain function) would do.
4. No default branch in `RunnableBranch` — unmatched input raises.

## Best practices
- Name intermediate values with dict outputs so traces are readable.
- Keep each step's prompt focused on one job; small steps are easier to test.
- Measure per-step latency (AgentForge records it in every trace).

## In this project
- `backend/src/chains/sequential.py` — outline → expand pipeline.
- `backend/src/chains/conditional.py` — sentiment-routed response chain (`RunnableBranch` + `RunnableLambda`).
- `backend/src/chains/parallel.py` — summary/keywords/tone via `RunnableParallel`.
