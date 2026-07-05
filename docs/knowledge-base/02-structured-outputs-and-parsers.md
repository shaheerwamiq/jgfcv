# Structured Outputs & Output Parsers

> Source: Full_Stack.pdf pp. 2–4 (structured response, Pydantic validation, `StrOutputParser`, `PydanticOutputParser`)

## What it is
Output parsers convert raw LLM text into usable data:
- **`StrOutputParser`** — the "cleaning and sanitizer tool": extracts plain string content from a model message so it can feed the next step of a chain.
- **`PydanticOutputParser`** — parses model output into a validated Pydantic model. It "adds intelligence" beyond organizing output: the parser injects format instructions into the prompt and validates the response against the schema.

## Why it exists
Applications need predictable data, not prose. Downstream code (APIs, databases, UI) cannot consume free-form text. Parsers make LLM output a typed contract.

## When to use it
- `StrOutputParser`: between every chain step where the next step expects a string ("neat predictable string for multistep workflows").
- `PydanticOutputParser` / structured output: whenever the answer must be machine-readable — classification labels, extracted fields, scores.

## When NOT to use it
- Pure creative generation shown directly to a human (a blog draft) — forcing JSON degrades quality.
- Very large outputs — JSON escaping of long text is fragile; return markdown and parse sections instead.

## Pros / Cons
| Pros | Cons |
| --- | --- |
| Type-safe, validated outputs | Extra prompt tokens for format instructions |
| Fails loudly on bad output (catchable) | Models occasionally emit invalid JSON — needs retry |
| Schema doubles as documentation | Over-constrained schemas reduce answer quality |

## Alternatives
- **Native structured output / function calling** (`llm.with_structured_output(Model)`) — uses the provider's JSON mode; generally more reliable than prompt-based parsing. AgentForge uses this where Gemini supports it.
- **JsonOutputParser** — parses JSON without Pydantic validation.
- **Regex post-processing** — brittle; last resort.

## Common beginner mistakes
1. Trusting the model to "always return JSON" without a parser or retry.
2. Not including `parser.get_format_instructions()` in the prompt.
3. Schemas with deeply nested optional fields — models fill them inconsistently.
4. Swallowing validation errors instead of retrying with the error message.

## Best practices
- Prefer provider-native structured output; fall back to `PydanticOutputParser`.
- Keep schemas flat and small; add `Field(description=...)` for every field.
- On validation failure, retry once with the validation error appended to the prompt.

## In this project
- `backend/src/chains/parsers.py` — both parser styles with a validating retry.
- `backend/src/agents/supervisor.py` — routing decision as a structured Pydantic output.
- `backend/src/agents/analyst_agent.py` — analysis returned as a validated schema.
