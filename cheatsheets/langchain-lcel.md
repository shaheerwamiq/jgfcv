# Cheatsheet: LangChain LCEL

## Core imports
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI
```

## The atoms
```python
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise analyst."),
    ("human", "{input}"),
])
chain = prompt | llm | StrOutputParser()
chain.invoke({"input": "..."})        # one call
chain.stream({"input": "..."})        # token stream
chain.batch([{"input": "a"}, ...])    # parallel batch
```

## Sequential (step N feeds step N+1)
```python
outline = outline_prompt | llm | StrOutputParser()
expand  = expand_prompt  | llm | StrOutputParser()
pipeline = outline | (lambda o: {"outline": o}) | expand
```

## Parallel (independent branches, merged dict)
```python
parallel = RunnableParallel(
    summary=sum_prompt | llm | StrOutputParser(),
    keywords=kw_prompt | llm | StrOutputParser(),
    tone=tone_prompt | llm | StrOutputParser(),
)
result = parallel.invoke({"text": text})   # {"summary": ..., "keywords": ..., "tone": ...}
```

## Conditional (route by predicate)
```python
branch = RunnableBranch(
    (lambda x: x["sentiment"] == "negative", apology_chain),
    (lambda x: x["sentiment"] == "positive", thanks_chain),
    neutral_chain,                    # default — ALWAYS provide one
)
full = classify_chain | branch
```

## RunnableLambda (plain Python as a chain step)
```python
clean = RunnableLambda(lambda s: s.strip().lower())
chain = prompt | llm | StrOutputParser() | clean
```

## Structured output (prefer native)
```python
class Verdict(BaseModel):
    label: str = Field(description="positive | negative | neutral")
    confidence: float

structured_llm = llm.with_structured_output(Verdict)   # native JSON mode
# fallback: PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=Verdict)
prompt = ChatPromptTemplate.from_template(
    "Classify: {text}\n{format_instructions}"
).partial(format_instructions=parser.get_format_instructions())
```

## Gotchas
- Missing `StrOutputParser()` → next step receives `AIMessage`, not `str`.
- `RunnableBranch` without a default → raises on unmatched input.
- Chains are DAGs: no loops. Loops/routing-at-runtime → LangGraph.
- Old import paths (`langchain.output_parser`) are dead → `langchain_core.output_parsers`.
