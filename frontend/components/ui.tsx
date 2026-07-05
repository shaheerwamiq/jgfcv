// Small shared UI primitives used across pages.

export function Card({
  children,
  className = '',
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={`rounded-lg border border-border bg-card p-5 ${className}`}>{children}</div>
  )
}

export function CardTitle({ children }: { children: React.ReactNode }) {
  return <h2 className="mb-3 text-sm font-semibold text-foreground">{children}</h2>
}

export function Badge({
  children,
  tone = 'default',
}: {
  children: React.ReactNode
  tone?: 'default' | 'success' | 'warning' | 'danger'
}) {
  const tones = {
    default: 'bg-muted text-muted-foreground',
    success: 'bg-accent text-accent-foreground',
    warning: 'bg-warning/15 text-warning',
    danger: 'bg-destructive/15 text-destructive',
  }
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 font-mono text-xs ${tones[tone]}`}>
      {children}
    </span>
  )
}

export function Button({
  children,
  variant = 'primary',
  className = '',
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost'
}) {
  const variants = {
    primary:
      'bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50',
    secondary:
      'border border-border bg-card text-foreground hover:bg-muted disabled:opacity-50',
    ghost: 'text-muted-foreground hover:text-foreground disabled:opacity-50',
  }
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}

export function Spinner() {
  return (
    <span
      className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
      role="status"
      aria-label="Loading"
    />
  )
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive"
    >
      {message}
    </div>
  )
}
