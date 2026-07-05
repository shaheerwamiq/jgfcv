# Learning Guide: Chains, Prompts & Parsers

Each concept explained at five levels: absolute beginner, practical, engineering, senior/system-design, and interview-ready — plus an analogy.

## Chains (LCEL)

**Level 1 — Beginner:** A chain is a to-do list for the AI. Instead of asking one giant question, you break work into small steps and pass each answer to the next step.

**Level 2 — Practical:** In code, `prompt | llm | StrOutputParser()` means: fill the template, send it to the model, extract the text. Add more `| prompt2 | llm` segments to build multi-step pipelines. Everything supports `.invoke()`, `.stream()`, `.batch()`.

**Level 3 — Engineering:** Every element is a `Runnable` implementing a uniform protocol; composition produces a new `Runnable`. This uniformity is why streaming and async propagate through the whole pipeline for free, and why tracing tools can instrument any chain without code changes.

**Level 4 — Senior:** Chains are DAGs — a deliberate constraint. It buys predictability (bounded cost/latency, easy testing) at the price of expressiveness (no cycles, no runtime re-routing). System design question to always ask: "does this workflow need to make decisions mid-flight?" If yes, you've outgrown chains — reach for a graph.

**Level 5 — Interview:** "LCEL composes Runnables with the pipe operator into declarative pipelines. I use sequential chains for dependent steps, `RunnableParallel` to cut wall-clock latency on independent steps, and `RunnableBranch` for input-dependent routing. When I need cycles or agent handoffs I move to LangGraph, because LCEL is intentionally acyclic."

**Analogy:** A chain is a factory assembly line: each station does one job and passes the item down the belt. A parallel chain is multiple belts running side by side that merge at packaging. What the line *cannot* do is send an item backward — for that you need a workshop (a graph) where a craftsman decides the next step each time.

## Prompt templates & chat history

**Level 1:** The AI forgets everything between messages. Chat history is you re-telling it the conversation so far. A template is a fill-in-the-blanks letter.

**Level 2:** `ChatPromptTemplate.from_messages([("system", ...), MessagesPlaceholder("history"), ("human", "{input}")])` — history is injected each call; the store just appends and windows messages per session.

**Level 3:** History grows O(turns) in tokens; production systems window (keep last N), summarize (LLM-compress old turns), or hybridize. Session scoping is a correctness *and* privacy requirement.

**Level 4:** Treat prompts as versioned artifacts (code-reviewed files, not inline strings). Prompt changes are deploys: they need diffs, rollbacks, and regression tests against a fixed eval set.

**Level 5 — Interview:** "LLMs are stateless; conversation memory is an application concern. I keep per-session windowed history, version system prompts in the repo, and never place user input into the system role — that's an injection vector."

**Analogy:** Talking to an LLM is like phoning a brilliant consultant with amnesia: every call, you must read them the minutes of all previous calls. The template is your standard briefing format.

## Output parsers

**Level 1:** The AI answers in a chatty paragraph, but your program needs tidy boxes: a label, a score, a list. A parser makes the AI fill in a form instead.

**Level 2:** `StrOutputParser` extracts the plain string (essential glue between chain steps). `PydanticOutputParser` generates format instructions from a schema and validates the response into a typed object; native `with_structured_output()` uses the provider's JSON mode and is usually more reliable.

**Level 3:** Validation failures are expected events, not exceptions to ignore: catch, append the validation error to the prompt, retry once. Keep schemas flat; describe every field — descriptions are prompt engineering.

**Level 4:** Structured output is the contract boundary between the probabilistic system (LLM) and the deterministic system (your app). Design schemas the way you design APIs: stable, minimal, versioned. Over-constraining hurts answer quality; measure both parse-rate and answer quality.

**Level 5 — Interview:** "I prefer provider-native structured output, falling back to `PydanticOutputParser` with a validation-error retry loop. The Pydantic schema doubles as the API contract and the test fixture — one source of truth from model output to HTTP response."

**Analogy:** Without a parser, asking an LLM for data is like asking a poet for your bank balance — the answer is in there, somewhere, beautifully phrased. A parser hands the poet a tax form with numbered boxes.
