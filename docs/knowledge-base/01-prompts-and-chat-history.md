# Prompts & Chat History

> Source: Full_Stack.pdf pp. 1–2 (`chat_history`, `ChatPromptTemplate`, context maintenance)

## What it is
Prompt templates are reusable, parameterized message structures (`ChatPromptTemplate`). Chat history is the ordered record of prior human/AI messages injected into the prompt so the model has conversational context.

## Why it exists
LLMs are stateless — every call starts from zero. Without replaying history, the model cannot resolve references like "expand on that". Templates prevent copy-pasted, injection-prone string formatting.

## When to use it
- Any multi-turn conversation (chatbots, assistants, agents).
- Any prompt with variable slots (user name, retrieved context, task input).

## When NOT to use it
- Single-shot transformations with no conversational state (classification, extraction) — a plain prompt is simpler.
- Very long conversations replayed verbatim — you will blow the context window; summarize or window the history instead.

## Pros / Cons
| Pros | Cons |
| --- | --- |
| Reusable, testable prompts | History grows linearly with turns (cost + latency) |
| Clear separation of system/human/AI roles | Naive replay can exceed context limits |
| Safe variable interpolation | Templates hide the final prompt unless you log it |

## Alternatives
- **Raw f-strings** — fine for scripts, unsafe and unmaintainable in production.
- **Summarization memory** — compress old turns with an LLM before injecting.
- **Windowed memory** — keep only the last N turns (what AgentForge does).

## Common beginner mistakes
1. Storing history globally instead of per-session (users see each other's chats).
2. Replaying unbounded history until the context window overflows.
3. Putting user input in the system message (prompt-injection risk).
4. Forgetting the `MessagesPlaceholder` so history is silently dropped.

## Best practices
- Scope history by session ID; cap the window (AgentForge keeps the last 20 messages).
- Keep the system prompt separate from and above user content.
- Version prompts as files (see `prompts/`) so changes are code-reviewed.

## In this project
- `backend/src/memory/chat_history.py` — session-scoped, windowed history store.
- `backend/src/agents/*.py` — each agent builds a `ChatPromptTemplate` with a system message + task input.
- `prompts/` — every system prompt versioned as markdown.
