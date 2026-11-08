import type { ReactNode } from 'react'

type AlertProps = {
  kind: 'error' | 'success' | 'info'
  children: ReactNode
}

export function Alert({ kind, children }: AlertProps) {
  return (
    <p className={`alert alert--${kind}`} role={kind === 'error' ? 'alert' : 'status'}>
      {children}
    </p>
  )
}
