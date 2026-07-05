"""Input guardrails: validate user input BEFORE it reaches the LLM.

Layered defence (cheap checks first):
1. Length limits           — bound cost and abuse surface.
2. Prompt-injection scan   — regex patterns for known jailbreak phrasings.
3. Secrets scan            — refuse inputs containing what look like API keys.

The course notes cover nemoguardrails (Colang) — a full DSL-based rails
engine. We implement the same *concept* as lightweight, dependency-free
rails; see docs/knowledge-base/08-guardrails.md for the comparison.
"""

import re

from src.core.config import get_settings
from src.schemas.models import GuardrailVerdict

# Common prompt-injection / jailbreak phrasings.
INJECTION_PATTERNS: list[tuple[str, str]] = [
    (r"ignore\s+(all\s+|your\s+)?(previous|prior|above)\s+(instructions|prompts?|rules)", "instruction-override attempt"),
    (r"disregard\s+(all\s+|your\s+)?(previous|prior|system)\s+(instructions|prompts?)", "instruction-override attempt"),
    (r"you\s+are\s+now\s+(dan|in\s+developer\s+mode|jailbroken)", "persona-hijack attempt"),
    (r"reveal\s+(your\s+)?(system\s+prompt|instructions|initial\s+prompt)", "system-prompt extraction attempt"),
    (r"repeat\s+(everything|all\s+text)\s+(above|before)", "system-prompt extraction attempt"),
    (r"pretend\s+(you\s+have\s+no|there\s+are\s+no)\s+(rules|restrictions|guidelines)", "restriction-bypass attempt"),
]

# Things that look like credentials being pasted in.
SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style API key"),
    (r"AIza[A-Za-z0-9_\-]{30,}", "Google API key"),
    (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", "private key material"),
]


def check_input(text: str) -> GuardrailVerdict:
    """Run all input rails; returns the first failure or a pass."""
    settings = get_settings()
    if not settings.guardrails_enabled:
        return GuardrailVerdict(passed=True, rail="disabled", reason="Guardrails disabled by config")

    stripped = text.strip()
    if not stripped:
        return GuardrailVerdict(passed=False, rail="length", reason="Input is empty")
    if len(stripped) > settings.max_input_chars:
        return GuardrailVerdict(
            passed=False,
            rail="length",
            reason=f"Input exceeds {settings.max_input_chars} characters",
        )

    lowered = stripped.lower()
    for pattern, label in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return GuardrailVerdict(passed=False, rail="prompt_injection", reason=f"Blocked: {label}")

    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, stripped):
            return GuardrailVerdict(passed=False, rail="secrets", reason=f"Blocked: input contains {label}")

    return GuardrailVerdict(passed=True, rail="all", reason="All input rails passed")
