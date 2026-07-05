import type { Metadata } from 'next'
import { DocumentManager } from '@/components/document-manager'

export const metadata: Metadata = {
  title: 'Documents — AgentForge',
  description: 'Ingest documents into the RAG pipeline: load, chunk, embed, index.',
}

export default function DocumentsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Document ingestion</h1>
        <p className="mt-1 max-w-2xl text-pretty text-sm leading-relaxed text-muted-foreground">
          The full RAG ingest pipeline: load a document, split it with
          RecursiveCharacterTextSplitter, embed each chunk with Gemini, and index in FAISS. Then
          query it directly to see retrieval scores.
        </p>
      </div>
      <DocumentManager />
    </div>
  )
}
