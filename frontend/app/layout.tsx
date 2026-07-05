import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import { Nav } from '@/components/nav'

const geistSans = Geist({ subsets: ['latin'], variable: '--font-geist-sans' })
const geistMono = Geist_Mono({ subsets: ['latin'], variable: '--font-geist-mono' })

export const metadata: Metadata = {
  title: 'AgentForge — Multi-Agent AI Workflow Platform',
  description:
    'Production-grade multi-agent AI platform built with LangChain, LangGraph, and Gemini. Supervisor-routed agents, RAG, guardrails, and full observability.',
}

export const viewport = {
  themeColor: '#0b0d0e',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`bg-background ${geistSans.variable} ${geistMono.variable}`}>
      <body className="min-h-screen font-sans antialiased">
        <Nav />
        <main className="mx-auto w-full max-w-6xl px-4 py-8 md:px-6">{children}</main>
      </body>
    </html>
  )
}
