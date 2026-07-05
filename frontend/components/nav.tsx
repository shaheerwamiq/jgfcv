'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { href: '/', label: 'Dashboard' },
  { href: '/workflow', label: 'Workflow' },
  { href: '/documents', label: 'Documents' },
  { href: '/playground', label: 'Playground' },
  { href: '/learn', label: 'Learn' },
]

export function Nav() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/90 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4 md:px-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded bg-primary font-mono text-sm font-bold text-primary-foreground">
            A
          </span>
          <span className="font-semibold tracking-tight">AgentForge</span>
        </Link>
        <nav aria-label="Main navigation" className="flex items-center gap-1 overflow-x-auto">
          {links.map((link) => {
            const active =
              link.href === '/' ? pathname === '/' : pathname.startsWith(link.href)
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded px-3 py-1.5 text-sm transition-colors ${
                  active
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {link.label}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
