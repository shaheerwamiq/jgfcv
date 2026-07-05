"""FAISS vector store manager (in-memory, process lifetime).

FAISS gives exact/approximate nearest-neighbour search over embeddings.
This manager wraps a single FAISS index plus a registry of ingested
documents so the API can list/delete them. In production you would use a
persistent store (Chroma, pgvector, Pinecone) — the LangChain VectorStore
interface makes that a drop-in swap.
"""

import threading

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.core.errors import DocumentNotFoundError
from src.llm.embeddings import get_embeddings


class VectorStoreManager:
    """Thread-safe wrapper around a lazily-created FAISS index."""

    def __init__(self) -> None:
        self._store: FAISS | None = None
        self._documents: dict[str, dict] = {}  # name -> {chunks, characters}
        self._lock = threading.Lock()

    @property
    def is_empty(self) -> bool:
        return self._store is None

    def add_chunks(self, name: str, chunks: list[Document]) -> None:
        """Embed chunks and add them to the index (creating it if needed)."""
        with self._lock:
            if self._store is None:
                self._store = FAISS.from_documents(chunks, get_embeddings())
            else:
                self._store.add_documents(chunks)
            chars = sum(len(c.page_content) for c in chunks)
            self._documents[name] = {"chunks": len(chunks), "characters": chars}

    def search(self, query: str, k: int = 4) -> list[tuple[Document, float]]:
        """Similarity search with scores (lower L2 distance = more similar)."""
        with self._lock:
            if self._store is None:
                raise DocumentNotFoundError("No documents have been ingested yet")
            return self._store.similarity_search_with_score(query, k=k)

    def as_retriever(self, k: int = 4):
        """LangChain retriever interface for use inside chains/agents."""
        with self._lock:
            if self._store is None:
                raise DocumentNotFoundError("No documents have been ingested yet")
            return self._store.as_retriever(search_kwargs={"k": k})

    def list_documents(self) -> list[dict]:
        with self._lock:
            return [
                {"name": name, **info} for name, info in sorted(self._documents.items())
            ]

    def reset(self) -> None:
        with self._lock:
            self._store = None
            self._documents.clear()


# Module-level singleton shared by routes and agents.
vector_store = VectorStoreManager()
