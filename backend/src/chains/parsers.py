"""Output parser demos: StrOutputParser vs PydanticOutputParser.

- StrOutputParser: extracts the raw text content from a model message.
- PydanticOutputParser: instructs the model to emit JSON matching a
  Pydantic schema, then parses + validates it. Guarantees structure at
  the cost of a slightly longer prompt (format instructions).
"""

import time

from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.llm.client import get_llm


class TextAnalysis(BaseModel):
    """Structured schema the model must fill in (PydanticOutputParser demo)."""

    summary: str = Field(description="One-sentence summary of the text")
    sentiment: str = Field(description="positive, negative, or neutral")
    topics: list[str] = Field(description="Up to 3 key topics")
    word_count: int = Field(description="Approximate word count of the input")


def run_str_parser(text: str) -> tuple[str, int]:
    """prompt | llm | StrOutputParser — plain text out."""
    start = time.time()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a concise analyst. Reply in 2-3 sentences."),
            ("human", "Analyze this text: {text}"),
        ]
    )
    chain = prompt | get_llm() | StrOutputParser()
    result = chain.invoke({"text": text})
    return result, int((time.time() - start) * 1000)


def run_pydantic_parser(text: str) -> tuple[dict, int]:
    """prompt | llm | PydanticOutputParser — validated structured output."""
    start = time.time()
    parser = PydanticOutputParser(pydantic_object=TextAnalysis)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an analyst. {format_instructions}"),
            ("human", "Analyze this text: {text}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())
    chain = prompt | get_llm(temperature=0.0) | parser
    result: TextAnalysis = chain.invoke({"text": text})
    return result.model_dump(), int((time.time() - start) * 1000)
