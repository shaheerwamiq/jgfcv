# Learning Guide: Agents, LangGraph & Multi-Agent Systems

## Agents

**Level 1 — Beginner:** A chain follows a fixed recipe. An agent is a chef who tastes as they cook and decides the next step themselves — maybe look something up, maybe ask a specialist, maybe finish.

**Level 2 — Practical:** An agent = LLM + tools + a loop. The model sees the task and available tools, picks an action, observes the result, repeats until done. In LangChain these are chain-based agents; LangGraph gives you explicit control over that loop as a graph.

**Level 3 — Engineering:** The loop must be bounded (max iterations), observable (log every action), and interruptible. Tool schemas are prompts too — good descriptions determine whether the right tool gets called. Agent state should be typed and minimal.

**Level 4 — Senior:** The core trade-off is autonomy vs. predictability. Every decision you delegate to the LLM adds flexibility and removes guarantees. Production posture: constrain the action space, cap iterations and budget, and design for the failure mode where the agent confidently does the wrong thing.

**Level 5 — Interview:** "An agent is an LLM making control-flow decisions at runtime over a set of tools. I use them only where runtime judgment is genuinely required, keep the action space small, bound the loop, and trace every step — otherwise a chain is simpler, cheaper, and testable."

**Analogy:** A chain is a train on rails — fast, safe, fixed route. An agent is a taxi driver — goes anywhere, but you're trusting their judgment in traffic.

## LangGraph & the supervisor pattern

**Level 1:** LangGraph is a flowchart for AI workers. Boxes are workers (agents), arrows say who works next, and a shared clipboard (state) is passed along.

**Level 2:** Define a `TypedDict` state, add nodes (functions/agents that read and update state), add edges — including conditional edges where a function (often an LLM decision) picks the next node. Compile, invoke, get final state.

**Level 3:** The supervisor pattern: a router node classifies the request (structured output!) and conditionally routes to specialist nodes. Each node appends to a trace list in state. Cycles are allowed — cap them via a counter in state.

**Level 4:** Graphs make implicit orchestration explicit and testable: you can unit-test routing logic without LLMs by stubbing the classifier, replay any run from its trace, and add checkpoints for durability/human-in-the-loop. That explicitness is the real production win over ad-hoc agent loops.

**Level 5 — Interview:** "LangGraph models multi-agent workflows as state machines: typed shared state, nodes as agents, conditional edges as routing. I use a supervisor that emits a structured routing decision, specialists that each do one job, and guardrails outside the graph boundary. Versus chains: graphs buy cycles and runtime routing at the cost of an extra routing call and more surface to test."

**Analogy:** LangGraph is a hospital triage system: the triage nurse (supervisor) assesses each patient (request) and routes to the right specialist. Every hand-off is logged on the patient's chart (state/trace), and the chart travels with the patient.

## Guardrails

**Level 1:** Guardrails are the bouncers of your AI app: one at the door checking what comes in, one at the exit checking what goes out.

**Level 2:** Input rails: pattern checks for prompt injection ("ignore previous instructions"), topic allow-lists. Output rails: PII regexes, policy screening. NeMo Guardrails formalizes this with Colang; lightweight custom rails cover most needs.

**Level 3:** Layer cheap-to-expensive: regex first (microseconds), LLM classifier only when inconclusive. Fail closed for risky actions. Log every verdict; maintain an attack test suite.

**Level 4:** The system prompt is not a security boundary — treat all model output as untrusted input to downstream systems. Injection via retrieved documents (indirect injection) is the sneaky one: your RAG corpus is an attack surface.

**Level 5 — Interview:** "Defense in depth: pattern rails, then LLM classification, then output screening for PII and grounding — with verdicts logged and surfaced in traces. I treat indirect injection through retrieved content as seriously as direct user input, and I fail closed on high-risk operations."

**Analogy:** A castle doesn't rely on asking visitors nicely to behave (the system prompt). It has a gate, guards, and a food taster — layered defenses, each catching what the previous missed.

## Observability

**Level 1:** If the AI gives a weird answer, you need a replay of everything that happened — like a flight recorder.

**Level 2:** Record per run: steps taken, which agent, prompts in/out, latency, token estimates, guardrail verdicts. LangSmith traces LLM calls; Logfire traces the whole app; structured logs + run IDs are the zero-dependency baseline.

**Level 3:** Correlate everything with a run ID. Track cost (tokens) alongside latency. Sample verbose traces in production; redact PII before shipping traces to third parties.

**Level 4:** Observability enables evaluation: once every run is a trace, you can build regression sets from real failures, A/B prompts against them, and catch quality drift. Traces are the raw material of LLM QA.

**Level 5 — Interview:** "Every workflow run gets a run ID and a step-level trace — agent, action, latency, tokens, guardrail verdicts — queryable via API and rendered in the UI. For scale I'd layer LangSmith for LLM-call detail and OpenTelemetry/Logfire for whole-app correlation."

**Analogy:** Running LLM apps without traces is like running an airline without black boxes: when something goes wrong, all you have is the crater and the customer complaints.
