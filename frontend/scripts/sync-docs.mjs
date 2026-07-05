// Copies repo-root learning content into frontend/content so the /learn
// pages can read it after the frontend service is built in isolation.
import fs from "node:fs"
import path from "node:path"

const here = path.dirname(new URL(import.meta.url).pathname)
const frontendRoot = path.resolve(here, "..")
const repoRoot = path.resolve(frontendRoot, "..")
const target = path.join(frontendRoot, "content")

const dirs = ["docs", "cheatsheets", "interview-notes"]

for (const dir of dirs) {
  const src = path.join(repoRoot, dir)
  if (!fs.existsSync(src)) continue
  const dest = path.join(target, dir)
  fs.rmSync(dest, { recursive: true, force: true })
  fs.cpSync(src, dest, { recursive: true })
  console.log(`[sync-docs] copied ${dir} -> content/${dir}`)
}
