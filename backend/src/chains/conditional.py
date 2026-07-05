"""Conditional chain: RunnableBranch routes by classification result.

Pattern from the notes:
    branch = RunnableBranch(
        (condition_1, chain_1),
        (condition_2, chain_2),
        default_chain,
    )
Here: classify sentiment first, then respond with a branch-specific chain.
"""

import time
from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda
from pydantic import BaseModel, Field

from src.llm.client import get_llm
from src.schemas.models import TraceStep


class SentimentResult(BaseModel):
    """Classifier output — constrained via Literal for safe branching."""

    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="Overall sentiment of the text"
    )


def run_conditional_chain(text: str) -> tuple[dict, list[TraceStep], int]:
    """Classify sentiment, then RunnableBranch to a tailored response chain."""
    start = time.time()
    llm = get_llm()
    parser = StrOutputParser()

    # Step 1: classification with a structured (Pydantic) output.
    clf_parser = PydanticOutputParser(pydantic_object=SentimentResult)
    clf_prompt = ChatPromptTemplate.from_template(
        "Classify the sentiment of this text.\n{format_instructions}\n\nText: {text}"
    ).partial(format_instructions=clf_parser.get_format_instructions())

    t1 = time.time()
    sentiment: SentimentResult = (clf_prompt | get_llm(temperature=0.0) | clf_parser).invoke(
        {"text": text}
    )
    clf_ms = int((time.time() - t1) * 1000)

    # Step 2: branch-specific response chains.
    positive_chain = (
        ChatPromptTemplate.from_template(
            "Write a warm thank-you reply to this positive feedback: {text}"
        )
        | llm
        | parser
    )
    negative_chain = (
        ChatPromptTemplate.from_template(
            "Write an empathetic, solution-oriented reply to this negative feedback: {text}"
        )
        | llm
        | parser
    )
    neutral_chain = (
        ChatPromptTemplate.from_template(
            "Write a brief, informative acknowledgement of this feedback: {text}"
        )
        | llm
        | parser
    )

    branch = RunnableBranch(
        (lambda x: x["sentiment"] == "positive", positive_chain),
        (lambda x: x["sentiment"] == "negative", negative_chain),
        neutral_chain,  # default branch
    )

    t2 = time.time()
    response = branch.invoke({"sentiment": sentiment.sentiment, "text": text})
    branch_ms = int((time.time() - t2) * 1000)

    steps = [
        TraceStep(step="classify_sentiment", agent="chain:conditional", detail=f"PydanticOutputParser -> '{sentiment.sentiment}'", latency_ms=clf_ms),
        TraceStep(step="route_branch", agent="chain:conditional", detail=f"RunnableBranch selected the '{sentiment.sentiment}' chain", latency_ms=0),
        TraceStep(step="generate_response", agent="chain:conditional", detail="branch chain | llm | StrOutputParser", latency_ms=branch_ms),
    ]
    output = {"sentiment": sentiment.sentiment, "response": response}
    return output, steps, int((time.time() - start) * 1000)


# RunnableLambda example (from the notes): wrap any python function as a Runnable.
word_counter = RunnableLambda(lambda x: {"words": len(str(x).split())})
