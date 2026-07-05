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
}

export default nextConfig
