import fs from "node:fs"
import path from "node:path"

/**
 * Learning content lives at the repository root (docs/, cheatsheets/,
 * interview-notes/) so it is readable on GitHub. In the sandbox / local
 * dev the frontend can read it via "..". For production builds the
 * prebuild script (scripts/sync-docs.mjs) copies it into content/.
 */
const ROOTS = ["..", "content"]

export interface DocEntry {
  /** URL slug segments, e.g. ["docs", "knowledge-base", "05-rag"] */
  slug: string[]
  /** Display title derived from the first markdown heading */
  title: string
  /** Section label, e.g. "Knowledge Base" */
  section: string
}

const SECTION_DIRS: { dir: string; section: string }[] = [
  { dir: "docs/knowledge-base", section: "Knowledge Base" },
  { dir: "docs/learning-guide", section: "Learning Guide" },
  { dir: "docs/architecture", section: "Architecture" },
  { dir: "docs", section: "Guides" },
  { dir: "cheatsheets", section: "Cheatsheets" },
  { dir: "interview-notes", section: "Interview Notes" },
]

function resolveBase(): string | null {
  for (const root of ROOTS) {
    const candidate = path.resolve(process.cwd(), root)
    if (fs.existsSync(path.join(candidate, "docs", "knowledge-base"))) {
      return candidate
    }
  }
  return null
}

function titleFromMarkdown(filePath: string, fallback: string): string {
  try {
    const raw = fs.readFileSync(filePath, "utf8")
    const match = raw.match(/^#\s+(.+)$/m)
    if (match) return match[1].trim()
  } catch {
    // fall through to fallback
  }
  return fallback
}

export function listDocs(): DocEntry[] {
  const base = resolveBase()
  if (!base) return []

  const entries: DocEntry[] = []
  const seen = new Set<string>()

  for (const { dir, section } of SECTION_DIRS) {
    const abs = path.join(base, dir)
    if (!fs.existsSync(abs)) continue
    for (const file of fs.readdirSync(abs).sort()) {
      if (!file.endsWith(".md")) continue
      const rel = path.join(dir, file)
      if (seen.has(rel)) continue
      seen.add(rel)
      const slug = rel.replace(/\.md$/, "").split(path.sep)
      entries.push({
        slug,
        section,
        title: titleFromMarkdown(path.join(abs, file), file.replace(/\.md$/, "")),
      })
    }
  }
  return entries
}

export function readDoc(slug: string[]): { title: string; content: string } | null {
  const base = resolveBase()
  if (!base) return null

  // Prevent path traversal: only allow simple path segments.
  if (slug.some((s) => !/^[\w.-]+$/.test(s))) return null

  const abs = path.join(base, ...slug) + ".md"
  const normalized = path.normalize(abs)
  if (!normalized.startsWith(base)) return null
  if (!fs.existsSync(normalized)) return null

  const content = fs.readFileSync(normalized, "utf8")
  const match = content.match(/^#\s+(.+)$/m)
  return { title: match ? match[1].trim() : slug[slug.length - 1], content }
}
