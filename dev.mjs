// Local development orchestrator.
// Starts the FastAPI backend (uvicorn, port 8000) and the Next.js frontend
// (port 3000). Next.js proxies /api/* to the backend in dev (see
// frontend/next.config.ts). In production, Vercel's experimentalServices
// routing (vercel.json) handles this instead.
import { spawn } from 'node:child_process'
import { readFileSync } from 'node:fs'

// Load project env vars (e.g. GOOGLE_API_KEY) for the backend process.
// Next.js loads .env.development.local natively; uvicorn does not.
const env = { ...process.env }
for (const file of ['.env.development.local', '.env']) {
  try {
    const raw = readFileSync(new URL(`./${file}`, import.meta.url), 'utf8')
    for (const line of raw.split('\n')) {
      const m = line.match(/^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/)
      if (!m) continue
      let value = m[2]
      if (
        (value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))
      ) {
        value = value.slice(1, -1)
      }
      if (!(m[1] in process.env)) env[m[1]] = value
    }
  } catch {
    // file not present — fine
  }
}

const procs = []

function run(name, cmd, args, cwd) {
  const child = spawn(cmd, args, {
    cwd: new URL(cwd, import.meta.url).pathname,
    stdio: 'inherit',
    env,
  })
  child.on('exit', (code) => {
    console.log(`[dev] ${name} exited with code ${code}`)
    // If one service dies, bring everything down so the runner restarts cleanly.
    for (const p of procs) {
      if (p !== child && p.exitCode === null) p.kill('SIGTERM')
    }
    process.exit(code ?? 1)
  })
  procs.push(child)
  return child
}

run('backend', 'uv', ['run', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'], './backend/')
run('frontend', 'npm', ['run', 'dev', '--', '--port', '3000'], './frontend/')

for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, () => {
    for (const p of procs) if (p.exitCode === null) p.kill('SIGTERM')
    process.exit(0)
  })
}
