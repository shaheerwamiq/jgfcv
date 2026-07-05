"""End-to-end RAG pipeline: retrieve -> augment -> generate.

Modern LCEL equivalent of the notes' RetrievalQA:
    {"context": retriever | format_docs, "question": passthrough}
    | prompt | llm | StrOutputParser
Grounding the model in retrieved chunks (and instructing it to say "I
don't know" otherwise) is the core hallucination defence.
"""

import time

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.core.config import get_settings
from src.llm.client import get_llm
from src.rag.vectorstore import vector_store

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a precise assistant. Answer ONLY from the provided context. "
            "If the context does not contain the answer, say \"I don't know based on "
            "the provided documents.\" Cite sources inline like [source].",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)


def format_docs(docs: list[Document]) -> str:
    """Render retrieved chunks into a single context block with source tags."""
    parts = []
    for doc in docs:
        src = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page")
        tag = f"{src} p.{page}" if page else src
        parts.append(f"[{tag}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def answer_question(question: str) -> tuple[str, list[tuple[Document, float]], int]:
    """Full RAG round-trip; returns answer + retrieved chunks + latency."""
    start = time.time()
    settings = get_settings()

    results = vector_store.search(question, k=settings.retriever_k)
    docs = [doc for doc, _score in results]

    chain = RAG_PROMPT | get_llm(temperature=0.0) | StrOutputParser()
    answer = chain.invoke({"context": format_docs(docs), "question": question})

    return answer, results, int((time.time() - start) * 1000)
