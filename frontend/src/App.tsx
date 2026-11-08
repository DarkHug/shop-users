import { useEffect } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { setSessionExpiredHandler } from './api/client'
import { hasTokens } from './auth/tokens'
import { RequireAuth } from './components/RequireAuth'
import { LoginPage } from './pages/LoginPage'
import { MePage } from './pages/MePage'
import { OAuthCallbackPage } from './pages/OAuthCallbackPage'
import { RegisterPage } from './pages/RegisterPage'

export function App() {
  const navigate = useNavigate()

  // Обёртка над fetch сообщает сюда, что обновить токены не удалось:
  // они уже вычищены, остаётся увести пользователя на вход.
  useEffect(() => {
    setSessionExpiredHandler(() => {
      navigate('/login', {
        replace: true,
        state: { message: 'Сессия истекла, войдите заново', kind: 'info' },
      })
    })
    return () => setSessionExpiredHandler(null)
  }, [navigate])

  return (
    <Routes>
      <Route path="/" element={<Navigate to={hasTokens() ? '/me' : '/login'} replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/auth/google/callback" element={<OAuthCallbackPage provider="google" />} />
      <Route path="/auth/github/callback" element={<OAuthCallbackPage provider="github" />} />
      <Route
        path="/me"
        element={
          <RequireAuth>
            <MePage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
