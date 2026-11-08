import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { login } from '../api/auth'
import { toMessage } from '../api/errors'
import { Alert } from '../components/Alert'
import { Field } from '../components/Field'
import { ProviderButtons } from '../components/ProviderButtons'

type NoticeKind = 'success' | 'info'
type LoginLocationState = { message?: string; kind?: NoticeKind } | null

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()

  // Сообщение, переданное через navigate: успешная регистрация, выход, истёкшая сессия.
  const incomingState = location.state as LoginLocationState
  const incoming = incomingState?.message ?? ''
  const incomingKind: NoticeKind = incomingState?.kind ?? 'success'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState(incoming)
  const [noticeKind] = useState<NoticeKind>(incomingKind)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setNotice('')
    try {
      await login(email, password)
      navigate('/me', { replace: true })
    } catch (caught) {
      setError(toMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <div className="card">
        <h1>Вход</h1>
        <p className="subtitle">prosto_shop — ручная проверка сценариев авторизации</p>

        {notice && <Alert kind={noticeKind}>{notice}</Alert>}
        {error && <Alert kind="error">{error}</Alert>}

        <form onSubmit={handleSubmit}>
          <Field
            id="email"
            label="Email"
            type="email"
            value={email}
            onChange={setEmail}
            autoComplete="email"
          />
          <Field
            id="password"
            label="Пароль"
            type="password"
            value={password}
            onChange={setPassword}
            autoComplete="current-password"
          />
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? 'Входим…' : 'Войти'}
          </button>
        </form>

        <div className="divider">или</div>
        <ProviderButtons onError={setError} />

        <p className="footer-link">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </div>
    </div>
  )
}
