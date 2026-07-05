import type { TraceStep } from '@/lib/api'

const statusStyles: Record<string, string> = {
  ok: 'bg-primary',
  blocked: 'bg-warning',
  error: 'bg-destructive',
  skipped: 'bg-muted-foreground',
}

const agentColors: Record<string, string> = {
  supervisor: 'text-primary',
  research: 'text-sky-400',
  analyst: 'text-amber-400',
  writer: 'text-rose-400',
  guardrails: 'text-muted-foreground',
}

function agentColor(agent: string) {
  const key = agent.split(':')[0]
  return agentColors[key] ?? 'text-muted-foreground'
}

export function TraceViewer({ trace }: { trace: TraceStep[] }) {
  if (!trace.length) return null
  return (
    <ol className="flex flex-col" aria-label="Execution trace">
      {trace.map((step, i) => (
        <li key={`${step.step}-${i}`} className="flex gap-3">
          <div className="flex flex-col items-center">
            <span
              className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${statusStyles[step.status] ?? 'bg-muted-foreground'}`}
              aria-hidden="true"
            />
            {i < trace.length - 1 && <span className="w-px flex-1 bg-border" aria-hidden="true" />}
          </div>
          <div className="flex-1 pb-4">
            <div className="flex flex-wrap items-baseline gap-x-2">
              <span className="font-mono text-sm text-foreground">{step.step}</span>
              <span className={`font-mono text-xs ${agentColor(step.agent)}`}>{step.agent}</span>
              {step.latency_ms > 0 && (
                <span className="font-mono text-xs text-muted-foreground">{step.latency_ms}ms</span>
              )}
            </div>
            <p className="mt-0.5 text-sm leading-relaxed text-muted-foreground">{step.detail}</p>
          </div>
        </li>
      ))}
    </ol>
  )
}
