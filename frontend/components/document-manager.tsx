'use client'

import { useState } from 'react'
import useSWR from 'swr'
import {
  fetcher,
  postJson,
  uploadFile,
  type DocumentInfo,
  type IngestResponse,
  type RagQueryResponse,
} from '@/lib/api'
import { Badge, Button, Card, CardTitle, ErrorNote, Spinner } from '@/components/ui'
import { Markdown } from '@/components/markdown'

export function DocumentManager() {
  const { data: docs, mutate } = useSWR<DocumentInfo[]>('/api/documents', fetcher)

  const [name, setName] = useState('')
  const [content, setContent] = useState('')
  const [ingesting, setIngesting] = useState(false)
  const [ingestResult, setIngestResult] = useState<IngestResponse | null>(null)
  const [ingestError, setIngestError] = useState('')

  const [question, setQuestion] = useState('')
  const [querying, setQuerying] = useState(false)
  const [queryResult, setQueryResult] = useState<RagQueryResponse | null>(null)
  const [queryError, setQueryError] = useState('')

  async function ingestText(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim() || !content.trim() || ingesting) return
    setIngesting(true)
    setIngestError('')
    setIngestResult(null)
    try {
      const result = await postJson<IngestResponse>('/api/documents/ingest-text', {
        name: name.trim(),
        content,
      })
      setIngestResult(result)
      setName('')
      setContent('')
      mutate()
    } catch (err) {
      setIngestError(err instanceof Error ? err.message : 'Ingestion failed')
    } finally {
      setIngesting(false)
    }
  }

  async function handleFile(file: File | undefined) {
    if (!file || ingesting) return
    setIngesting(true)
    setIngestError('')
    setIngestResult(null)
    try {
      const result = await uploadFile('/api/documents/upload', file)
      setIngestResult(result)
      mutate()
    } catch (err) {
      setIngestError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setIngesting(false)
    }
  }

  async function runQuery(e: React.FormEvent) {
    e.preventDefault()
    if (!question.trim() || querying) return
    setQuerying(true)
    setQueryError('')
    setQueryResult(null)
    try {
      const result = await postJson<RagQueryResponse>('/api/documents/query', {
        question,
      })
      setQueryResult(result)
    } catch (err) {
      setQueryError(err instanceof Error ? err.message : 'Query failed')
    } finally {
      setQuerying(false)
    }
  }

  async function clearIndex() {
    await fetch('/api/documents', { method: 'DELETE' })
    setQueryResult(null)
    setIngestResult(null)
    mutate()
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Card>
          <CardTitle>Ingest text</CardTitle>
          <form onSubmit={ingestText} className="flex flex-col gap-3">
            <label htmlFor="doc-name" className="sr-only">
              Document name
            </label>
            <input
              id="doc-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Document name (e.g. product-notes.md)"
              className="w-full rounded-md border border-border bg-input px-3 py-2 text-sm placeholder:text-muted-foreground focus:border-primary focus:outline-none"
            />
            <label htmlFor="doc-content" className="sr-only">
              Document content
            </label>
            <textarea
              id="doc-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={6}
              placeholder="Paste document content here…"
              className="w-full resize-y rounded-md border border-border bg-input px-3 py-2 text-sm leading-relaxed placeholder:text-muted-foreground focus:border-primary focus:outline-none"
            />
            <div className="flex items-center justify-between gap-3">
              <label className="cursor-pointer rounded-md border border-border px-3 py-2 text-xs text-muted-foreground transition-colors hover:border-primary hover:text-foreground">
                Upload .txt / .md / .pdf
                <input
                  type="file"
                  accept=".txt,.md,.pdf"
                  className="sr-only"
                  onChange={(e) => handleFile(e.target.files?.[0])}
                />
              </label>
              <Button type="submit" disabled={ingesting || !name.trim() || !content.trim()}>
                {ingesting ? <Spinner /> : null}
                {ingesting ? 'Ingesting…' : 'Ingest'}
              </Button>
            </div>
          </form>
          {ingestError && (
            <div className="mt-3">
              <ErrorNote message={ingestError} />
            </div>
          )}
          {ingestResult && (
            <div className="mt-4 rounded-md border border-border bg-muted p-4">
              <p className="text-sm">
                Indexed <span className="font-mono text-primary">{ingestResult.name}</span>
              </p>
              <p className="mt-1 font-mono text-xs text-muted-foreground">
                {ingestResult.chunks} chunks · {ingestResult.characters} chars · avg{' '}
                {ingestResult.avg_chunk_chars} chars/chunk
              </p>
              <div className="mt-3 flex flex-col gap-2">
                {ingestResult.sample_chunks.map((chunk, i) => (
                  <p
                    key={i}
                    className="rounded border border-border bg-card p-2 font-mono text-xs leading-relaxed text-muted-foreground"
                  >
                    {chunk}
                    {chunk.length >= 220 ? '…' : ''}
                  </p>
                ))}
              </div>
            </div>
          )}
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <CardTitle>Indexed documents</CardTitle>
            {docs && docs.length > 0 && (
              <Button variant="ghost" onClick={clearIndex} className="text-xs">
                Clear index
              </Button>
            )}
          </div>
          {docs && docs.length > 0 ? (
            <ul className="flex flex-col gap-2">
              {docs.map((doc) => (
                <li
                  key={doc.name}
                  className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
                >
                  <span className="truncate font-mono text-xs">{doc.name}</span>
                  <span className="shrink-0 font-mono text-xs text-muted-foreground">
                    {doc.chunks} chunks
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">Nothing indexed yet.</p>
          )}
        </Card>
      </div>

      <Card className="self-start">
        <CardTitle>Query the index (RAG)</CardTitle>
        <form onSubmit={runQuery} className="flex flex-col gap-3">
          <label htmlFor="rag-question" className="sr-only">
            Question
          </label>
          <textarea
            id="rag-question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={2}
            placeholder="Ask a question about the indexed documents…"
            className="w-full resize-y rounded-md border border-border bg-input px-3 py-2 text-sm leading-relaxed placeholder:text-muted-foreground focus:border-primary focus:outline-none"
          />
          <Button type="submit" disabled={querying || !question.trim()} className="self-end">
            {querying ? <Spinner /> : null}
            {querying ? 'Retrieving…' : 'Query'}
          </Button>
        </form>
        {queryError && (
          <div className="mt-3">
            <ErrorNote message={queryError} />
          </div>
        )}
        {queryResult && (
          <div className="mt-4 flex flex-col gap-4">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <p className="text-xs font-semibold text-muted-foreground">Answer</p>
                <Badge>{queryResult.latency_ms}ms</Badge>
              </div>
              <Markdown content={queryResult.answer} />
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold text-muted-foreground">
                Retrieved chunks (lower score = closer match)
              </p>
              <div className="flex flex-col gap-2">
                {queryResult.chunks.map((chunk, i) => (
                  <div key={i} className="rounded-md border border-border bg-muted p-3">
                    <div className="mb-1 flex items-center justify-between">
                      <span className="font-mono text-xs text-primary">{chunk.source}</span>
                      {chunk.score !== null && (
                        <span className="font-mono text-xs text-muted-foreground">
                          L2 {chunk.score}
                        </span>
                      )}
                    </div>
                    <p className="font-mono text-xs leading-relaxed text-muted-foreground">
                      {chunk.content}
                      {chunk.content.length >= 400 ? '…' : ''}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
