'use client'

// Interactive playground: chain demos, parser comparison, embedding similarity.

import { useState } from 'react'
import {
  postJson,
  type ChainDemoResponse,
  type ParserDemoResponse,
  type SimilarityResponse,
} from '@/lib/api'
import { Badge, Button, Card, CardTitle, ErrorNote, Spinner } from '@/components/ui'
import { TraceViewer } from '@/components/trace-viewer'

type Tab = 'chains' | 'parsers' | 'embeddings'

const TABS: { id: Tab; label: string }[] = [
  { id: 'chains', label: 'Chains' },
  { id: 'parsers', label: 'Parsers' },
  { id: 'embeddings', label: 'Embeddings' },
]

export function PlaygroundTabs() {
  const [tab, setTab] = useState<Tab>('chains')

  return (
    <div className="flex flex-col gap-6">
      <div
        role="tablist"
        aria-label="Playground modes"
        className="flex gap-1 rounded-lg border border-border bg-card p-1"
      >
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              tab === t.id
                ? 'bg-muted text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      {tab === 'chains' && <ChainsTab />}
      {tab === 'parsers' && <ParsersTab />}
      {tab === 'embeddings' && <EmbeddingsTab />}
    </div>
  )
}

function ChainsTab() {
  const [chainType, setChainType] = useState<'sequential' | 'conditional' | 'parallel'>(
    'sequential',
  )
  const [text, setText] = useState('Remote work has changed how software teams collaborate.')
  const [result, setResult] = useState<ChainDemoResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      setResult(
        await postJson<ChainDemoResponse>('/api/chains/demo', { chain_type: chainType, text }),
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <CardTitle>Chain patterns (LCEL)</CardTitle>
        <p className="mb-4 text-sm leading-relaxed text-muted-foreground">
          Sequential pipes steps one after another. Conditional routes with RunnableBranch based on
          classified sentiment. Parallel fans out with RunnableParallel and merges results.
        </p>
        <div className="mb-3 flex flex-wrap gap-2">
          {(['sequential', 'conditional', 'parallel'] as const).map((c) => (
            <Button
              key={c}
              variant={chainType === c ? 'primary' : 'secondary'}
              onClick={() => setChainType(c)}
            >
              {c}
            </Button>
          ))}
        </div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
          aria-label="Chain input text"
          className="mb-3 w-full rounded-md border border-border bg-background p-3 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        />
        <Button onClick={run} disabled={loading || text.trim().length === 0}>
          {loading ? <Spinner /> : null} Run {chainType} chain
        </Button>
      </Card>
      {error && <ErrorNote message={error} />}
      {result && (
        <>
          <Card>
            <CardTitle>Output</CardTitle>
            <div className="flex flex-col gap-3">
              {Object.entries(result.output).map(([step, value]) => (
                <div key={step}>
                  <Badge>{step}</Badge>
                  <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                    {value}
                  </p>
                </div>
              ))}
            </div>
            <p className="mt-3 font-mono text-xs text-muted-foreground">
              {result.latency_ms}ms total
            </p>
          </Card>
          <TraceViewer trace={result.steps} />
        </>
      )}
    </div>
  )
}

function ParsersTab() {
  const [text, setText] = useState(
    'The new dashboard release improved load times by 40% but users report the dark theme has contrast issues.',
  )
  const [strResult, setStrResult] = useState<ParserDemoResponse | null>(null)
  const [pydanticResult, setPydanticResult] = useState<ParserDemoResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      const [s, p] = await Promise.all([
        postJson<ParserDemoResponse>('/api/parsers/demo', { parser: 'str', text }),
        postJson<ParserDemoResponse>('/api/parsers/demo', { parser: 'pydantic', text }),
      ])
      setStrResult(s)
      setPydanticResult(p)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <CardTitle>StrOutputParser vs PydanticOutputParser</CardTitle>
        <p className="mb-4 text-sm leading-relaxed text-muted-foreground">
          The same text is analyzed twice: once as free text (StrOutputParser) and once as a
          schema-validated object (PydanticOutputParser). Structured output gives you a contract.
        </p>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
          aria-label="Parser input text"
          className="mb-3 w-full rounded-md border border-border bg-background p-3 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        />
        <Button onClick={run} disabled={loading || text.trim().length === 0}>
          {loading ? <Spinner /> : null} Compare parsers
        </Button>
      </Card>
      {error && <ErrorNote message={error} />}
      {(strResult || pydanticResult) && (
        <div className="grid gap-4 md:grid-cols-2">
          {strResult && (
            <Card>
              <CardTitle>StrOutputParser → plain string</CardTitle>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                {String(strResult.output)}
              </p>
              <p className="mt-3 font-mono text-xs text-muted-foreground">
                {strResult.latency_ms}ms
              </p>
            </Card>
          )}
          {pydanticResult && (
            <Card>
              <CardTitle>PydanticOutputParser → validated object</CardTitle>
              <pre className="overflow-x-auto rounded-md bg-background p-3 font-mono text-xs leading-relaxed text-foreground">
                {JSON.stringify(pydanticResult.output, null, 2)}
              </pre>
              <p className="mt-3 font-mono text-xs text-muted-foreground">
                {pydanticResult.latency_ms}ms
              </p>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

function EmbeddingsTab() {
  const [texts, setTexts] = useState<string[]>([
    'The cat sat on the mat.',
    'A feline rested on the rug.',
    'Quarterly revenue grew by 12 percent.',
  ])
  const [result, setResult] = useState<SimilarityResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const updateText = (i: number, value: string) => {
    setTexts((prev) => prev.map((t, idx) => (idx === i ? value : t)))
  }

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      setResult(
        await postJson<SimilarityResponse>('/api/embeddings/similarity', {
          texts: texts.filter((t) => t.trim().length > 0),
        }),
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  const tone = (v: number) => {
    if (v >= 0.9) return 'text-primary'
    if (v >= 0.7) return 'text-foreground'
    return 'text-muted-foreground'
  }

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <CardTitle>Embedding similarity</CardTitle>
        <p className="mb-4 text-sm leading-relaxed text-muted-foreground">
          Each text is embedded with Gemini text-embedding-004, then compared pairwise with cosine
          similarity. Semantically similar sentences score close to 1.0 even with no shared words.
        </p>
        <div className="mb-3 flex flex-col gap-2">
          {texts.map((t, i) => (
            <input
              key={i}
              value={t}
              onChange={(e) => updateText(i, e.target.value)}
              aria-label={`Text ${i + 1}`}
              className="w-full rounded-md border border-border bg-background px-3 py-2 font-mono text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={run} disabled={loading}>
            {loading ? <Spinner /> : null} Compute similarity
          </Button>
          {texts.length < 5 && (
            <Button variant="secondary" onClick={() => setTexts((prev) => [...prev, ''])}>
              Add text
            </Button>
          )}
          {texts.length > 2 && (
            <Button variant="ghost" onClick={() => setTexts((prev) => prev.slice(0, -1))}>
              Remove last
            </Button>
          )}
        </div>
      </Card>
      {error && <ErrorNote message={error} />}
      {result && (
        <Card>
          <CardTitle>
            Cosine similarity matrix ({result.dimensions}-dim vectors, {result.latency_ms}ms)
          </CardTitle>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="p-2 text-left font-mono text-xs text-muted-foreground">Text</th>
                  {result.texts.map((_, i) => (
                    <th key={i} className="p-2 text-right font-mono text-xs text-muted-foreground">
                      T{i + 1}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.matrix.map((row, i) => (
                  <tr key={i} className="border-t border-border">
                    <td
                      className="max-w-48 truncate p-2 font-mono text-xs text-muted-foreground"
                      title={result.texts[i]}
                    >
                      T{i + 1}: {result.texts[i]}
                    </td>
                    {row.map((v, j) => (
                      <td key={j} className={`p-2 text-right font-mono text-xs ${tone(v)}`}>
                        {v.toFixed(3)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
