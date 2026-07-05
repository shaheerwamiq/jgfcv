import type { Metadata } from "next"
import { PlaygroundTabs } from "@/components/playground-tabs"

export const metadata: Metadata = {
  title: "Playground — AgentForge",
  description:
    "Experiment with LCEL chains, output parsers, and embedding similarity interactively.",
}

export default function PlaygroundPage() {
  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-8 md:px-8">
      <header className="mb-8">
        <p className="font-mono text-xs uppercase tracking-widest text-primary">
          Playground
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-balance">
          Chains, Parsers &amp; Embeddings
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          Run individual building blocks in isolation: sequential LCEL chains,
          structured output parsing with Pydantic, and cosine similarity over
          Gemini embeddings.
        </p>
      </header>
      <PlaygroundTabs />
    </main>
  )
}
