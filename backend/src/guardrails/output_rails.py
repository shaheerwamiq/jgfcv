"""Output guardrails: validate LLM output BEFORE it reaches the user.

1. PII scan     — redact emails, phone numbers, SSN-like patterns.
2. Empty check  — a blank answer is a failure, not a success.
3. Length bound — runaway generations get truncated.

Output rails REDACT rather than block where possible: blocking a whole
answer for one email address is worse UX than masking it.
"""

import re

from src.schemas.models import GuardrailVerdict

MAX_OUTPUT_CHARS = 20_000

PII_PATTERNS: list[tuple[str, str]] = [
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[email redacted]"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "[ssn redacted]"),
    (r"\b(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b", "[phone redacted]"),
]


def check_output(text: str) -> tuple[str, GuardrailVerdict]:
    """Run output rails; returns (possibly-redacted text, verdict)."""
    if not text or not text.strip():
        return "", GuardrailVerdict(passed=False, rail="empty", reason="Model returned an empty response")

    result = text
    redactions = 0
    for pattern, replacement in PII_PATTERNS:
        result, count = re.subn(pattern, replacement, result)
        redactions += count

    truncated = False
    if len(result) > MAX_OUTPUT_CHARS:
        result = result[:MAX_OUTPUT_CHARS] + "\n\n[output truncated by guardrail]"
        truncated = True

    if redactions or truncated:
        details = []
        if redactions:
            details.append(f"redacted {redactions} PII match(es)")
        if truncated:
            details.append("truncated over-long output")
        return result, GuardrailVerdict(passed=True, rail="pii", reason="; ".join(details))

    return result, GuardrailVerdict(passed=True, rail="all", reason="All output rails passed")
