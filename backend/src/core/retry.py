"""Retry with exponential backoff for flaky upstream calls (LLM APIs)."""

import random
import time
from collections.abc import Callable
from typing import TypeVar

from src.core.logging import get_logger

T = TypeVar("T")
logger = get_logger("core.retry")


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Call `fn`, retrying on failure with jittered exponential backoff.

    Jitter avoids the "thundering herd" problem where many clients retry
    at exactly the same instant after an outage.
    """
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except retry_on as exc:  # noqa: PERF203
            last_error = exc
            if attempt == attempts:
                break
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            delay *= 0.5 + random.random()  # jitter in [0.5x, 1.5x)
            logger.warning(
                "retryable failure, backing off",
                extra={"ctx": {"attempt": attempt, "delay_s": round(delay, 2), "error": str(exc)}},
            )
            time.sleep(delay)
    assert last_error is not None
    raise last_error
