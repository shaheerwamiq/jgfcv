import type { Metadata } from "next"
import Link from "next/link"
import { listDocs } from "@/lib/docs"

export const metadata: Metadata = {
  title: "Learn — AgentForge",
  description:
    "Knowledge base, learning guide, cheatsheets, and interview notes for the AgentForge stack.",
}

export const dynamic = "force-dynamic"

export default function LearnPage() {
  const docs = listDocs()
  const sections = Array.from(new Set(docs.map((d) => d.section)))

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-8 md:px-8">
      <header className="mb-8">
        <p className="font-mono text-xs uppercase tracking-widest text-primary">
          Learn
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-balance">
          Knowledge Base &amp; Learning Materials
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          Every concept in this platform is documented: per-topic knowledge base,
          five-level learning guide, cheatsheets, and interview preparation notes.
          All content also lives in the repository under docs/, cheatsheets/, and
          interview-notes/.
        </p>
      </header>

      {docs.length === 0 ? (
        <p className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
          No documentation found. Run <code className="font-mono">node scripts/sync-docs.mjs</code>{" "}
          from the frontend directory to sync content.
        </p>
      ) : (
        <div className="flex flex-col gap-10">
          {sections.map((section) => (
            <section key={section} aria-label={section}>
              <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-muted-foreground">
                {section}
              </h2>
              <ul className="grid grid-cols-1 gap-2 md:grid-cols-2">
                {docs
                  .filter((d) => d.section === section)
                  .map((doc) => (
                    <li key={doc.slug.join("/")}>
                      <Link
                        href={`/learn/${doc.slug.join("/")}`}
                        className="block rounded-lg border border-border bg-card px-4 py-3 text-sm text-card-foreground transition-colors hover:border-primary/50 hover:bg-secondary"
                      >
                        {doc.title}
                      </Link>
                    </li>
                  ))}
              </ul>
            </section>
          ))}
        </div>
      )}
    </main>
  )
}
