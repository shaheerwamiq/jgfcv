"""Structured JSON logging.

Production systems need machine-parseable logs. Each record is a single
JSON line with a timestamp, level, logger name, message, and any extra
context passed via the `extra={"ctx": {...}}` convention.
"""

import json
import logging
import sys
import time


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts": round(time.time(), 3),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        ctx = getattr(record, "ctx", None)
        if isinstance(ctx, dict):
            payload["ctx"] = ctx
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(debug: bool = False) -> None:
    """Install the JSON formatter on the root logger (idempotent)."""
    root = logging.getLogger()
    if any(isinstance(h.formatter, JsonFormatter) for h in root.handlers):
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.handlers = [handler]
    root.setLevel(logging.DEBUG if debug else logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Namespaced logger accessor."""
    return logging.getLogger(name)
