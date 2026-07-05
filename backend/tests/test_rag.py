"""RAG component tests — loaders and splitter (no embedding/LLM calls)."""

import pytest

from src.core.errors import ValidationFailedError
from src.rag.loaders import load_text
from src.rag.pipeline import format_docs
from src.rag.splitter import chunk_stats, split_documents


class TestLoaders:
    def test_load_text_wraps_document(self):
        docs = load_text("notes.txt", "Hello world content")
        assert len(docs) == 1
        assert docs[0].metadata["source"] == "notes.txt"

    def test_empty_text_rejected(self):
        with pytest.raises(ValidationFailedError):
            load_text("empty.txt", "   ")


class TestSplitter:
    def test_short_doc_single_chunk(self):
        docs = load_text("short.txt", "A short document.")
        chunks = split_documents(docs)
        assert len(chunks) == 1

    def test_long_doc_multiple_chunks_with_overlap(self):
        paragraph = "This is a sentence about machine learning systems. " * 60
        docs = load_text("long.txt", paragraph)
        chunks = split_documents(docs)
        assert len(chunks) > 1
        # Every chunk respects the configured max size (800 by default).
        assert all(len(c.page_content) <= 800 for c in chunks)
        # Metadata is preserved through splitting.
        assert all(c.metadata["source"] == "long.txt" for c in chunks)

    def test_chunk_stats(self):
        docs = load_text("s.txt", "word " * 500)
        chunks = split_documents(docs)
        stats = chunk_stats(chunks)
        assert stats["chunks"] == len(chunks)
        assert stats["avg_chunk_chars"] > 0

    def test_chunk_stats_empty(self):
        assert chunk_stats([])["chunks"] == 0


class TestFormatDocs:
    def test_sources_tagged(self):
        docs = load_text("guide.md", "Content here")
        formatted = format_docs(docs)
        assert "[guide.md]" in formatted
        assert "Content here" in formatted
