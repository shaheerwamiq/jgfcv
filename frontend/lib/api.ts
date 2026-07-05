// Typed client for the AgentForge backend. All calls go to /api/* — Vercel
// routes them to the Python service and strips the prefix.

export interface TraceStep {
  step: string
  agent: string
  detail: string
  latency_ms: number
  status: 'ok' | 'blocked' | 'error' | 'skipped'
}

export interface GuardrailVerdict {
  passed: boolean
  rail: string
  reason: string
}

export interface WorkflowResponse {
  answer: string
  agent: string
  route_reason: string
  sources: string[]
  trace: TraceStep[]
  input_guardrail: GuardrailVerdict
  output_guardrail: GuardrailVerdict
  total_latency_ms: number
}

export interface IngestResponse {
  name: string
  chunks: number
  characters: number
  avg_chunk_chars: number
  sample_chunks: string[]
}

export interface DocumentInfo {
  name: string
  chunks: number
  characters: number
}

export interface RagQueryResponse {
  answer: string
  chunks: { content: string; source: string; score: number | null }[]
  latency_ms: number
}

export interface ChainDemoResponse {
  chain_type: string
  output: Record<string, string>
  steps: TraceStep[]
  latency_ms: number
}

export interface ParserDemoResponse {
  parser: string
  output: Record<string, unknown> | string
  latency_ms: number
}

export interface SimilarityResponse {
  texts: string[]
  matrix: number[][]
  dimensions: number
  latency_ms: number
}

export interface RunSummary {
  run_id: string
  kind: string
  agent: string
  input_preview: string
  status: string
  total_latency_ms: number
  timestamp: number
  trace: TraceStep[]
}

export interface ObservabilityResponse {
  runs: RunSummary[]
  cache: { entries: number; hits: number; misses: number }
  totals: { runs: number; avg_latency_ms: number; errors: number }
}

export interface HealthResponse {
  status: string
  app: string
  llm_model: string
  embedding_model: string
  api_key_configured: boolean
  guardrails_enabled: boolean
  documents_indexed: number
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const body = await res.json()
      message = body?.error?.message ?? body?.detail?.[0]?.msg ?? message
    } catch {
      // keep default message
    }
    throw new Error(message)
  }
  return res.json() as Promise<T>
}

export const fetcher = <T,>(url: string): Promise<T> => fetch(url).then((r) => handle<T>(r))

export function postJson<T>(url: string, body: unknown): Promise<T> {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then((r) => handle<T>(r))
}

export function uploadFile(url: string, file: File): Promise<IngestResponse> {
  const form = new FormData()
  form.append('file', file)
  return fetch(url, { method: 'POST', body: form }).then((r) => handle<IngestResponse>(r))
}
