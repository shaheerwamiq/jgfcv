"""Embedding model factory + cosine similarity.

The course notes used HuggingFace sentence-transformers (all-MiniLM-L6-v2)
which requires torch — far too heavy for serverless deployment. We use
Gemini's hosted embedding API instead; the interface (embed_documents /
embed_query) is identical, so swapping back is a one-line change.
See docs/knowledge-base/04-embeddings-and-similarity.md for the trade-offs.
"""

from functools import lru_cache

import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.core.config import get_settings


@lru_cache
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Build (and cache) the Gemini embedding model."""
    settings = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key or None,
    )


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors, in [-1, 1].

    cos(theta) = (a . b) / (|a| * |b|)
    1.0 = identical direction, 0.0 = orthogonal (unrelated), -1.0 = opposite.
    """
    va, vb = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0.0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def similarity_matrix(vectors: list[list[float]]) -> list[list[float]]:
    """Pairwise cosine similarity matrix for a list of vectors."""
    return [[round(cosine_similarity(a, b), 4) for b in vectors] for a in vectors]
