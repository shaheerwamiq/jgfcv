# Learning Guide — Start Here

A structured path through everything in this repository, from zero to interview-ready.

## The map

```
Prompts & History → Parsers → Chains (LCEL) → Embeddings → Vector Stores → RAG
                                                                        ↓
                    Observability ← Guardrails ← Multi-Agent (LangGraph)
```

## Recommended path

### Week 1 — Foundations
1. Read `knowledge-base/01-prompts-and-chat-history.md` and `02-structured-outputs-and-parsers.md`.
2. Open the **Playground** page: run the Structured Parser tab; compare input text with the validated JSON.
3. Read the code: `backend/src/chains/parsers.py` (50 lines — read all of it).
4. Deep-dive: `learning-guide/chains-and-parsers.md` levels 1–3.

### Week 2 — Chains
1. Read `knowledge-base/03-chains-lcel.md`.
2. Playground → Sequential Chain tab; watch a topic become an outline, then an expansion.
3. Read `backend/src/chains/sequential.py`, `conditional.py`, `parallel.py` — note the `|` composition and where `StrOutputParser` sits.
4. Exercise: sketch a 3-step chain for "review code → find bugs → suggest fixes". Which steps could be parallel?

### Week 3 — Embeddings & RAG
1. Read `knowledge-base/04`, `05`, `06`.
2. Playground → Embedding Similarity: try "How do I reset my password?" against 4 candidate sentences; observe scores.
3. **Documents** page: upload a text file, watch chunk counts, then ask questions and check the citations.
4. Read `backend/src/rag/` end to end (4 small files).
5. Deep-dive: `learning-guide/rag-and-embeddings.md`.

### Week 4 — Agents, Guardrails, Observability
1. Read `knowledge-base/07`, `08`, `09`, `10`.
2. **Workflow** page: run "Summarize the key risks of prompt injection" and study the trace — supervisor route, agent steps, guardrail verdicts, latencies.
3. Try to trip the input rails ("ignore all previous instructions and ...") and watch the verdict.
4. Read `backend/src/agents/graph.py` and `supervisor.py`; then `guardrails/`.
5. Deep-dive: `learning-guide/agents-and-graphs.md`.

### Prepare for interviews
- Work through `interview-notes/questions.md` — say answers out loud.
- Skim all `cheatsheets/` the day before.
- Be ready to whiteboard: the RAG pipeline, the supervisor graph, and the guardrail layers (all diagrammed in `architecture/ARCHITECTURE.md`).

## How the app and docs cross-reference
Every knowledge-base page ends with an "In this project" section pointing to the exact source files, and every major backend module's docstring points back to its knowledge-base page.
