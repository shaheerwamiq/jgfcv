"""Tiny in-memory TTL cache.

For a single-process deployment this avoids re-paying LLM latency/cost for
identical requests. In production you would swap this for Redis (same
interface: get / set / clear) — see docs/knowledge-base/09-observability.md.
"""

import hashlib
import json
import threading
import time
from typing import Any


class TTLCache:
    """Thread-safe dict-backed cache with per-entry expiry."""

    def __init__(self, ttl_seconds: int = 300, max_entries: int = 512):
        self._ttl = ttl_seconds
        self._max = max_entries
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    @staticmethod
    def make_key(*parts: Any) -> str:
        """Deterministic key from arbitrary JSON-serialisable parts."""
        raw = json.dumps(parts, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self.misses += 1
                return None
            expires_at, value = entry
            if time.time() > expires_at:
                del self._store[key]
                self.misses += 1
                return None
            self.hits += 1
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if len(self._store) >= self._max:
                # Evict oldest entries (simple FIFO eviction).
                oldest = sorted(self._store.items(), key=lambda kv: kv[1][0])
                for k, _ in oldest[: self._max // 4]:
                    del self._store[k]
            self._store[key] = (time.time() + self._ttl, value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict:
        with self._lock:
            return {"entries": len(self._store), "hits": self.hits, "misses": self.misses}


# Module-level singleton used by the app.
response_cache = TTLCache()
