import Link from "next/link"
import { notFound } from "next/navigation"
import { readDoc } from "@/lib/docs"
import { Markdown } from "@/components/markdown"

export const dynamic = "force-dynamic"

export default async function DocPage({
  params,
}: {
  params: Promise<{ slug: string[] }>
}) {
  const { slug } = await params
  const doc = readDoc(slug)
  if (!doc) notFound()

  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-8 md:px-8">
      <nav aria-label="Breadcrumb" className="mb-6">
        <Link
          href="/learn"
          className="font-mono text-xs uppercase tracking-widest text-primary hover:underline"
        >
          {"<- All docs"}
        </Link>
      </nav>
      <article>
        <Markdown content={doc.content} />
      </article>
    </main>
  )
}
