"""Chunking with RecursiveCharacterTextSplitter.

Why recursive? It tries to split on paragraph boundaries first, then
sentences, then words — preserving semantic units instead of cutting
mid-sentence. Overlap keeps context that straddles a boundary retrievable
from either chunk.
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import get_settings


def split_documents(docs: list[Document]) -> list[Document]:
    """Split documents into overlapping chunks using configured sizes."""
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)


def chunk_stats(chunks: list[Document]) -> dict:
    """Summary stats about a chunk set (for the ingest UI)."""
    if not chunks:
        return {"chunks": 0, "characters": 0, "avg_chunk_chars": 0}
    total = sum(len(c.page_content) for c in chunks)
    return {
        "chunks": len(chunks),
        "characters": total,
        "avg_chunk_chars": total // len(chunks),
    }
