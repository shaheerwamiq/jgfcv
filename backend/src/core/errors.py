"""Domain error hierarchy.

A small, explicit hierarchy lets API handlers map failures to correct
HTTP status codes without leaking stack traces to clients.
"""


class AgentForgeError(Exception):
    """Base class for all domain errors."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str = "An internal error occurred"):
        self.message = message
        super().__init__(message)


class ValidationFailedError(AgentForgeError):
    """Client sent input that failed validation."""

    status_code = 422
    code = "validation_failed"


class GuardrailViolationError(AgentForgeError):
    """Input or output was blocked by a guardrail."""

    status_code = 400
    code = "guardrail_violation"


class DocumentNotFoundError(AgentForgeError):
    """Requested document / index does not exist."""

    status_code = 404
    code = "document_not_found"


class LLMUnavailableError(AgentForgeError):
    """Upstream LLM call failed after retries."""

    status_code = 502
    code = "llm_unavailable"
