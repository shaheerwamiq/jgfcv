"use client"

import { useState } from "react"
import useSWRMutation from "swr/mutation"
import {
  runChain,
  runParser,
  runEmbeddingSimilarity,
  type ChainResult,
  type ParserResult,
  type SimilarityResult,
} from "@/lib/api"
import { Button, Card, ErrorNote, Spinner, Textarea } from "@/components/ui"
import { Markdown } from "@/components/markdown"

type Tab = "chain" | "parser" | "embeddings"

const TABS: { id: Tab; label: string }[] = [
  { id: "chain", label: "Sequential Chain" },
  { id: "parser", label: "Structured Parser" },
  { id: "embeddings", label: "Embedding Similarity" },
]

export function PlaygroundTabs() {
  const [tab, setTab] = useState<Tab>("chain")

  return (
    <div>
      <div
        role="tablist"
        aria-label="Playground modes"
        className="flex flex-wrap gap-2 border-b border-border pb-3"
      >
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={`rounded-md px-3 py-1.5 font-mono text-xs transition-colors ${
              tab === t.id
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-muted"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="pt-6">
        {tab === "chain" && <ChainPanel />}
        {tab === "parser" && <ParserPanel />}
        {tab === "embeddings" && <EmbeddingsPanel />}
      </div>
    </div>
  )
}

function ChainPanel() {
  const [topic, setTopic] = useState("")
  const { trigger, data, error, isMutating } = useSWRMutation(
    "playground/chain",
    (_key, { arg }: { arg: string }) => runChain(arg),
  )
  const result = data as ChainResult | undefined

  return (
    <div className="flex flex-col gap-4">
      <Card
        title="Sequential chain: outline → expand"
        subtitle="prompt | llm | StrOutputParser piped into a second prompt"
      >
        <div className="flex flex-col gap-3">
          <Textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a topic, e.g. vector databases"
            rows={2}
            aria-label="Chain topic"
          />
          <div>
            <Button
              onClick={() => topic.trim() && trigger(topic.trim())}
              disabled={isMutating || !topic.trim()}
            >
              {isMutating ? <Spinner label="Running chain" /> : "Run chain"}
            </Button>
          </div>
        </div>
      </Card>
      {error && <ErrorNote error={error} />}
      {result && (
        <>
          <Card title="Step 1 — Outline" subtitle={`${result.latency_ms} ms total`}>
            <Markdown content={result.outline} />
          </Card>
          <Card title="Step 2 — Expanded">
            <Markdown content={result.expanded} />
          </Card>
        </>
      )}
    </div>
  )
}

function ParserPanel() {
  const [text, setText] = useState("")
  const { trigger, data, error, isMutating } = useSWRMutation(
    "playground/parser",
    (_key, { arg }: { arg: string }) => runParser(arg),
  )
  const result = data as ParserResult | undefined

  return (
    <div className="flex flex-col gap-4">
      <Card
        title="PydanticOutputParser"
        subtitle="Free text in, validated JSON out (sentiment, topics, summary)"
      >
        <div className="flex flex-col gap-3">
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste any text to analyze, e.g. a product review"
            rows={4}
            aria-label="Text to parse"
          />
          <div>
            <Button
              onClick={() => text.trim() && trigger(text.trim())}
              disabled={isMutating || !text.trim()}
            >
              {isMutating ? <Spinner label="Parsing" /> : "Parse to structured output"}
            </Button>
          </div>
        </div>
      </Card>
      {error && <ErrorNote error={error} />}
      {result && (
        <Card title="Validated output" subtitle={`${result.latency_ms} ms`}>
          <pre className="overflow-x-auto rounded-md bg-secondary p-4 font-mono text-xs leading-relaxed text-secondary-foreground">
            {JSON.stringify(result.parsed, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  )
}

function EmbeddingsPanel() {
  const [query, setQuery] = useState("")
  const [candidates, setCandidates] = useState("")
  const { trigger, data, error, isMutating } = useSWRMutation(
    "playground/embeddings",
    (_key, { arg }: { arg: { query: string; candidates: string[] } }) =>
      runEmbeddingSimilarity(arg.query, arg.candidates),
  )
  const result = data as SimilarityResult | undefined

  const parsedCandidates = candidates
    .split("\n")
    .map((c) => c.trim())
    .filter(Boolean)

  return (
    <div className="flex flex-col gap-4">
      <Card
        title="Cosine similarity"
        subtitle="Embed a query and candidate sentences, rank by similarity"
      >
        <div className="flex flex-col gap-3">
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Query sentence, e.g. How do I reset my password?"
            rows={2}
            aria-label="Query sentence"
          />
          <Textarea
            value={candidates}
            onChange={(e) => setCandidates(e.target.value)}
            placeholder={"One candidate sentence per line (2-8 lines)"}
            rows={4}
            aria-label="Candidate sentences"
          />
          <div>
            <Button
              onClick={() =>
                query.trim() &&
                parsedCandidates.length >= 2 &&
                trigger({ query: query.trim(), candidates: parsedCandidates })
              }
              disabled={isMutating || !query.trim() || parsedCandidates.length < 2}
            >
              {isMutating ? <Spinner label="Embedding" /> : "Rank by similarity"}
            </Button>
          </div>
        </div>
      </Card>
      {error && <ErrorNote error={error} />}
      {result && (
        <Card
          title="Ranked results"
          subtitle={`model: ${result.model} · dim: ${result.dimensions} · ${result.latency_ms} ms`}
        >
          <ol className="flex flex-col gap-2">
            {result.results.map((r) => (
              <li
                key={r.text}
                className="flex items-center justify-between gap-4 rounded-md bg-secondary px-3 py-2"
              >
                <span className="text-sm text-secondary-foreground">{r.text}</span>
                <span className="shrink-0 font-mono text-xs text-primary">
                  {r.score.toFixed(4)}
                </span>
              </li>
            ))}
          </ol>
        </Card>
      )}
    </div>
  )
}
