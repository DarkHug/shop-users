import type { ReactElement } from 'react'
import { Navigate } from 'react-router-dom'
import { hasTokens } from '../auth/tokens'

/** Без токенов защищённую страницу не показываем — сразу на /login. */
export function RequireAuth({ children }: { children: ReactElement }) {
  if (!hasTokens()) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ message: 'Войдите, чтобы открыть профиль', kind: 'info' }}
      />
    )
  }
  return children
}
