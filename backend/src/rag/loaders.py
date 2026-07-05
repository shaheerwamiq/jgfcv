"""Document loading: raw text and PDF bytes -> LangChain Documents.

The notes used TextLoader for files on disk; in a web API we receive
uploads as bytes, so these loaders adapt that pattern. pypdf handles PDF
extraction (the notes compare pypdf vs pymupdf — pypdf is pure-python and
deploys anywhere, pymupdf is faster but has native deps).
"""

import io

from langchain_core.documents import Document
from pypdf import PdfReader

from src.core.errors import ValidationFailedError


def load_text(name: str, content: str) -> list[Document]:
    """Wrap raw text as a single Document with source metadata."""
    cleaned = content.strip()
    if not cleaned:
        raise ValidationFailedError("Document content is empty")
    return [Document(page_content=cleaned, metadata={"source": name})]


def load_pdf_bytes(name: str, data: bytes) -> list[Document]:
    """Extract text from PDF bytes, one Document per page (keeps page metadata)."""
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as exc:
        raise ValidationFailedError(f"Could not read PDF: {exc}") from exc

    docs: list[Document] = []
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if text:
            docs.append(Document(page_content=text, metadata={"source": name, "page": i + 1}))
    if not docs:
        raise ValidationFailedError("PDF contained no extractable text (it may be scanned images)")
    return docs
