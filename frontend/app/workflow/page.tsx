import type { Metadata } from 'next'
import { WorkflowRunner } from '@/components/workflow-runner'

export const metadata: Metadata = {
  title: 'Workflow — AgentForge',
  description: 'Run multi-agent workflows with live routing, guardrails, and execution traces.',
}

export default function WorkflowPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Workflow runner</h1>
        <p className="mt-1 max-w-2xl text-pretty text-sm leading-relaxed text-muted-foreground">
          Send a request through the full pipeline: input guardrails, supervisor routing,
          specialist agent execution, output guardrails. The trace shows exactly what happened.
        </p>
      </div>
      <WorkflowRunner />
    </div>
  )
}
