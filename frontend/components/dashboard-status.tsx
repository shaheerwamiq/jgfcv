'use client'

import useSWR from 'swr'
import { fetcher, type HealthResponse, type ObservabilityResponse } from '@/lib/api'
import { Badge, Card, CardTitle } from '@/components/ui'

export function DashboardStatus() {
  const { data: health } = useSWR<HealthResponse>('/api/health', fetcher, {
    refreshInterval: 15000,
  })
  const { data: obs } = useSWR<ObservabilityResponse>('/api/observability?limit=8', fetcher, {
    refreshInterval: 10000,
  })

  return (
    <section aria-label="System status" className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardTitle>System status</CardTitle>
        {health ? (
          <dl className="flex flex-col gap-2 text-sm">
            <div className="flex items-center justify-between">
              <dt className="text-muted-foreground">Backend</dt>
              <dd>
                <Badge tone="success">{health.status}</Badge>
              </dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-muted-foreground">LLM model</dt>
              <dd className="font-mono text-xs">{health.llm_model}</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-muted-foreground">Embedding model</dt>
              <dd className="font-mono text-xs">{health.embedding_model}</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-muted-foreground">API key</dt>
              <dd>
                <Badge tone={health.api_key_configured ? 'success' : 'danger'}>
                  {health.api_key_configured ? 'configured' : 'missing'}
                </Badge>
              </dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-muted-foreground">Guardrails</dt>
              <dd>
                <Badge tone={health.guardrails_enabled ? 'success' : 'warning'}>
                  {health.guardrails_enabled ? 'enabled' : 'disabled'}
                </Badge>
              </dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-muted-foreground">Documents indexed</dt>
              <dd className="font-mono text-xs">{health.documents_indexed}</dd>
            </div>
          </dl>
        ) : (
          <p className="text-sm text-muted-foreground">Connecting to backend…</p>
        )}
      </Card>

      <Card>
        <CardTitle>Recent runs</CardTitle>
        {obs && obs.runs.length > 0 ? (
          <ul className="flex flex-col gap-2">
            {obs.runs.slice(0, 6).map((run) => (
              <li key={run.run_id} className="flex items-center justify-between gap-3 text-sm">
                <div className="min-w-0 flex-1">
                  <span className="font-mono text-xs text-primary">{run.agent}</span>
                  <p className="truncate text-muted-foreground">{run.input_preview}</p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <Badge tone={run.status === 'ok' ? 'success' : 'warning'}>{run.status}</Badge>
                  <span className="font-mono text-xs text-muted-foreground">
                    {run.total_latency_ms}ms
                  </span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">
            No runs yet — try the workflow or playground pages.
          </p>
        )}
        {obs && (
          <p className="mt-3 border-t border-border pt-3 font-mono text-xs text-muted-foreground">
            {obs.totals.runs} total runs · avg {obs.totals.avg_latency_ms}ms · cache{' '}
            {obs.cache.hits} hits / {obs.cache.misses} misses
          </p>
        )}
      </Card>
    </section>
  )
}
