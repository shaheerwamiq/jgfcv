import Link from 'next/link'
import { DashboardStatus } from '@/components/dashboard-status'

const agents = [
  {
    name: 'Supervisor',
    role: 'Router',
    color: 'text-primary',
    description:
      'Classifies each request with structured output and routes it to the right specialist via LangGraph conditional edges.',
    tech: 'LangGraph · PydanticOutputParser',
  },
  {
    name: 'Research',
    role: 'RAG specialist',
    color: 'text-sky-400',
    description:
      'Answers questions grounded in your uploaded documents: retrieve from FAISS, augment the prompt, generate with citations.',
    tech: 'FAISS · Gemini embeddings · LCEL',
  },
  {
    name: 'Analyst',
    role: 'Structured analysis',
    color: 'text-amber-400',
    description:
      'Produces schema-validated analyses — key points, pros, cons, verdict — enforced by a Pydantic output parser.',
    tech: 'PydanticOutputParser · typed chains',
  },
  {
    name: 'Writer',
    role: 'Composition',
    color: 'text-rose-400',
    description:
      'Composes summaries, emails, and explanations with session chat history injected via MessagesPlaceholder.',
    tech: 'ChatPromptTemplate · chat history',
  },
]

const pipeline = [
  'Input guardrails',
  'Supervisor routes',
  'Agent executes',
  'Output guardrails',
  'Trace recorded',
]

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-3">
        <p className="font-mono text-xs uppercase tracking-widest text-primary">
          LangChain · LangGraph · Gemini
        </p>
        <h1 className="max-w-2xl text-balance text-3xl font-semibold tracking-tight md:text-4xl">
          Multi-agent AI workflows with guardrails and full observability
        </h1>
        <p className="max-w-2xl text-pretty leading-relaxed text-muted-foreground">
          AgentForge routes every request through a supervisor to specialist agents — RAG
          research, structured analysis, and composition — with input/output guardrails and a
          complete execution trace for every run.
        </p>
        <div className="mt-2 flex flex-wrap gap-3">
          <Link
            href="/workflow"
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            Run a workflow
          </Link>
          <Link
            href="/learn"
            className="rounded-md border border-border bg-card px-4 py-2 text-sm font-medium transition-colors hover:bg-muted"
          >
            Browse the learning docs
          </Link>
        </div>
      </section>

      <section aria-label="Request pipeline" className="rounded-lg border border-border bg-card p-5">
        <h2 className="mb-4 text-sm font-semibold">Every request flows through</h2>
        <ol className="flex flex-col gap-2 md:flex-row md:items-center md:gap-0">
          {pipeline.map((stage, i) => (
            <li key={stage} className="flex items-center gap-2 md:flex-1">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent font-mono text-xs text-accent-foreground">
                {i + 1}
              </span>
              <span className="text-sm text-muted-foreground">{stage}</span>
              {i < pipeline.length - 1 && (
                <span className="mx-3 hidden h-px flex-1 bg-border md:block" aria-hidden="true" />
              )}
            </li>
          ))}
        </ol>
      </section>

      <section aria-label="Agents" className="grid gap-4 md:grid-cols-2">
        {agents.map((agent) => (
          <div key={agent.name} className="rounded-lg border border-border bg-card p-5">
            <div className="flex items-baseline justify-between">
              <h2 className={`font-mono text-sm font-semibold ${agent.color}`}>{agent.name}</h2>
              <span className="text-xs text-muted-foreground">{agent.role}</span>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{agent.description}</p>
            <p className="mt-3 font-mono text-xs text-muted-foreground/70">{agent.tech}</p>
          </div>
        ))}
      </section>

      <DashboardStatus />
    </div>
  )
}
