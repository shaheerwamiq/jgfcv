"""Core utility tests: cache, retry, similarity math, chat history."""

import pytest

from src.core.cache import TTLCache
from src.core.retry import retry_with_backoff
from src.llm.embeddings import cosine_similarity, similarity_matrix
from src.memory.chat_history import ChatHistoryStore


class TestTTLCache:
    def test_set_and_get(self):
        cache = TTLCache(ttl_seconds=60)
        cache.set("k", {"a": 1})
        assert cache.get("k") == {"a": 1}

    def test_miss_returns_none(self):
        cache = TTLCache()
        assert cache.get("missing") is None

    def test_expiry(self):
        cache = TTLCache(ttl_seconds=0)
        cache.set("k", "v")
        assert cache.get("k") is None

    def test_deterministic_keys(self):
        assert TTLCache.make_key("a", [1, 2]) == TTLCache.make_key("a", [1, 2])
        assert TTLCache.make_key("a") != TTLCache.make_key("b")


class TestRetry:
    def test_succeeds_first_try(self):
        assert retry_with_backoff(lambda: 42) == 42

    def test_retries_then_succeeds(self):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ValueError("transient")
            return "ok"

        assert retry_with_backoff(flaky, attempts=3, base_delay=0.01) == "ok"
        assert calls["n"] == 3

    def test_raises_after_exhaustion(self):
        def always_fails():
            raise ValueError("permanent")

        with pytest.raises(ValueError):
            retry_with_backoff(always_fails, attempts=2, base_delay=0.01)


class TestSimilarity:
    def test_identical_vectors(self):
        assert cosine_similarity([1, 0, 1], [1, 0, 1]) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        assert cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1.0)

    def test_zero_vector_safe(self):
        assert cosine_similarity([0, 0], [1, 1]) == 0.0

    def test_matrix_shape_and_diagonal(self):
        m = similarity_matrix([[1, 0], [0, 1], [1, 1]])
        assert len(m) == 3 and all(len(row) == 3 for row in m)
        for i in range(3):
            assert m[i][i] == pytest.approx(1.0)


class TestChatHistory:
    def test_append_and_get(self):
        store = ChatHistoryStore()
        store.append_exchange("s1", "hello", "hi there")
        history = store.get("s1")
        assert len(history) == 2
        assert history[0].content == "hello"

    def test_sessions_isolated(self):
        store = ChatHistoryStore()
        store.append_exchange("a", "q", "r")
        assert store.get("b") == []

    def test_trimming(self):
        store = ChatHistoryStore()
        for i in range(20):
            store.append_exchange("s", f"q{i}", f"r{i}")
        assert len(store.get("s")) == 20  # 10 turns * 2 messages

    def test_clear(self):
        store = ChatHistoryStore()
        store.append_exchange("s", "q", "r")
        store.clear("s")
        assert store.get("s") == []
