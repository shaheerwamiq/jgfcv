# Cheatsheet: FastAPI (for AI backends)

## App factory + router pattern (as used in backend/main.py)
```python
from fastapi import FastAPI, APIRouter

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(req: WorkflowRequest):
    return await execute(req)

app = FastAPI(title="AgentForge API")
app.include_router(router)
```

## Validation for free
```python
class WorkflowRequest(BaseModel):
    input: str = Field(min_length=1, max_length=8000)
    session_id: str = "default"
```
Bad body → automatic 422 with field-level errors. `response_model` filters/validates output.

## Error handling
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

raise HTTPException(status_code=404, detail="Run not found")

@app.exception_handler(AppError)                    # domain errors → clean JSON
async def app_error_handler(request, exc: AppError):
    return JSONResponse(status_code=exc.status_code,
                        content={"error": exc.message})
```

## File upload (documents endpoint)
```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    raw = await file.read()          # bytes; check content_type & size first
```

## Async rules of thumb
- `async def` + `await` for I/O (LLM calls, HTTP, DB).
- CPU-heavy / sync-only libs: `def` endpoint (runs in threadpool) or `run_in_executor`.
- Never block the event loop with sync LLM SDK calls inside `async def`.

## LLM-backend specifics
- Set explicit timeouts on all LLM calls; add retry with exponential backoff for 429/5xx.
- Return trace/run IDs in responses so the UI can fetch details.
- Health endpoint should check config presence, not make paid LLM calls.
- CORS: same-origin via gateway (Vercel `/api` prefix) needs no CORS config at all.

## Docs for free
`/docs` (Swagger) and `/openapi.json` generated from your Pydantic schemas.
