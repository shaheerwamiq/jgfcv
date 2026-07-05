# Guardrails

> Source: AI_compressed.pdf p. 1 ("Guardrails — appropriate & approved input, compliant output"; "nemoguardrails (rails are rules and regulations) — uses expression language colang")

## What it is
Guardrails enforce that input is "appropriate & approved" and output is "compliant". Rails are rules and regulations applied around the model:
- **Input rails** — block prompt injection, off-topic or disallowed requests before they reach the LLM.
- **Output rails** — check responses for PII leaks, policy violations, or ungrounded claims before they reach the user.

**NeMo Guardrails** (NVIDIA) is the well-known framework; it defines rails in **Colang**, a dialogue-flow expression language. **Guardrails AI** validates structured output against schemas with validators.

## Why it exists
LLMs will follow malicious instructions embedded in user input ("ignore previous instructions..."), leak data, and answer out-of-scope questions confidently. A single system prompt is not a security boundary.

## When to use it
- Anything user-facing, always. At minimum: injection screening on input, PII screening on output.
- Regulated domains (health, finance, legal) — add topical rails and refusal policies.

## When NOT to use it (heavily)
- Internal dev tools where friction outweighs risk — keep rails light.
- Don't use LLM-based rails on every request if latency is critical — layer pattern checks first.

## Defense-in-depth layers
1. **Pattern rails** — regex/keyword checks: instant, free, catches the obvious (this project's first layer).
2. **LLM classifier rails** — a small/fast model judges intent: catches paraphrases (this project's second layer, used when patterns are inconclusive).
3. **Structural checks** — output length, format, PII regexes (emails, phone numbers, keys).
4. **Grounding checks** — is the answer supported by retrieved context?

## Pros / Cons
| Pros | Cons |
| --- | --- |
| Blocks injection and leaks | Adds latency (esp. LLM rails) |
| Auditable verdicts per request | False positives frustrate users |
| Policy as code, testable | Rails themselves can be attacked — keep them simple |

## Alternatives
- **nemoguardrails + Colang** — full dialog-flow rails; heavyweight dependency, powerful for conversation policies. AgentForge implements lightweight custom rails instead (documented trade-off) and covers Colang concepts here.
- **Provider safety settings** — coarse content filters; combine, don't rely solely.

## Common beginner mistakes
1. Relying on the system prompt alone ("do not reveal X") — trivially bypassed.
2. Only guarding input, never output.
3. Failing open: if the rail errors, the request proceeds unchecked. Fail closed for high-risk actions.
4. Not logging verdicts — you cannot tune what you cannot see.

## Best practices
- Layer cheap checks before expensive ones; short-circuit on clear verdicts.
- Return the verdict in the trace (AgentForge shows guardrail verdicts in the workflow UI).
- Maintain a test suite of known attacks (`backend/tests/test_guardrails.py`).

## In this project
- `backend/src/guardrails/input_rails.py` — injection patterns + topic check with LLM fallback.
- `backend/src/guardrails/output_rails.py` — PII regexes + compliance screening.
