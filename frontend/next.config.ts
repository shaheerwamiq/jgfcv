import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  // The /learn docs browser reads markdown from the repo root at runtime.
  outputFileTracingIncludes: {
    '/learn': ['../docs/**/*', '../cheatsheets/**/*', '../interview-notes/**/*'],
    '/learn/**': ['../docs/**/*', '../cheatsheets/**/*', '../interview-notes/**/*'],
  },
  // In local development the FastAPI backend runs on port 8000. In production,
  // Vercel's experimentalServices routing forwards /api/* to the backend service,
  // so this rewrite only applies in dev.
  async rewrites() {
    if (process.env.NODE_ENV !== 'development') return []
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/:path*',
      },
    ]
  },
}

export default nextConfig
