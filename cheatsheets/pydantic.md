# Cheatsheet: Pydantic

Used by LangChain, CrewAI, AutoGen, FastAPI — the validation backbone of the Python AI stack.

## Models & fields
```python
from pydantic import BaseModel, Field, field_validator

class Analysis(BaseModel):
    sentiment: str = Field(description="positive | negative | neutral")
    confidence: float = Field(ge=0, le=1)
    topics: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("sentiment")
    @classmethod
    def check_sentiment(cls, v: str) -> str:
        allowed = {"positive", "negative", "neutral"}
        if v not in allowed:
            raise ValueError(f"must be one of {allowed}")
        return v
```

## Parse / dump
```python
a = Analysis.model_validate({"sentiment": "positive", "confidence": 0.9})
a = Analysis.model_validate_json('{"sentiment": "positive", "confidence": 0.9}')
a.model_dump()          # dict
a.model_dump_json()     # str
Analysis.model_json_schema()   # JSON Schema — what LLM JSON modes consume
```

## With LLMs
```python
# Field descriptions ARE prompt engineering — the model reads them.
structured = llm.with_structured_output(Analysis)
result: Analysis = structured.invoke("Review: great product, slow shipping")
```

## Settings (used in backend/src/core/config.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_api_key: str = ""
    model_name: str = "gemini-2.0-flash"

    class Config:
        env_file = ".env"
```

## FastAPI integration (free validation)
```python
@app.post("/analyze")
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    ...   # body already validated; response schema enforced & documented
```

## v1 → v2 renames (common interview trap)
| v1 | v2 |
| --- | --- |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `.parse_obj()` | `.model_validate()` |
| `@validator` | `@field_validator` |
| `class Config` | `model_config = ConfigDict(...)` (Config still works in pydantic-settings) |

## The Pydantic family (from the notes)
- **pydantic** — validation
- **pydantic-ai** — typed agent framework
- **logfire** — whole-app tracing (OpenTelemetry)
