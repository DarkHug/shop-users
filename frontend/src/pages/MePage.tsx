import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, logout, refreshTokensManually, type User } from '../api/auth'
import { SessionExpiredError, toMessage } from '../api/errors'
import { Alert } from '../components/Alert'
import { getAccessToken, getRefreshToken, subscribeTokens } from '../auth/tokens'

function preview(token: string | null): string {
  if (!token) return '—'
  return token.length <= 24 ? token : `${token.slice(0, 12)}…${token.slice(-8)}`
}

export function MePage() {
  const navigate = useNavigate()

  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [tokenTick, setTokenTick] = useState(0)

  // Перерисовываем панель токенов, когда обёртка над fetch их обновила.
  useEffect(() => subscribeTokens(() => setTokenTick((tick) => tick + 1)), [])

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      setUser(await getMe())
    } catch (caught) {
      // Если refresh не удался, клиент уже вычистил токены и App увёл на /login;
      // показывать ошибку здесь уже незачем.
      if (!(caught instanceof SessionExpiredError)) setError(toMessage(caught))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  async function handleLogout() {
    setBusy(true)
    try {
      // Токены чистятся внутри независимо от ответа сервера.
      await logout()
    } catch (caught) {
      console.warn('logout на бэкенде не прошёл, локальные токены всё равно удалены:', caught)
    } finally {
      setBusy(false)
      navigate('/login', { replace: true, state: { message: 'Вы вышли из аккаунта' } })
    }
  }

  async function handleManualRefresh() {
    setBusy(true)
    setError('')
    setNotice('')
    try {
      await refreshTokensManually()
      setNotice('Пара токенов обновлена')
    } catch (caught) {
      setError(toMessage(caught))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <div className="card card--wide">
        <h1>Профиль</h1>
        <p className="subtitle">GET /users/me</p>

        {notice && <Alert kind="success">{notice}</Alert>}
        {error && <Alert kind="error">{error}</Alert>}

        {loading && <Alert kind="info">Загружаем данные…</Alert>}

        {user && (
          <dl className="data-list">
            <dt>id</dt>
            <dd>{user.id}</dd>
            <dt>username</dt>
            <dd>{user.username ?? <span className="muted-note">не задан (вход через OAuth)</span>}</dd>
            <dt>email</dt>
            <dd>{user.email}</dd>
            <dt>is_verified</dt>
            <dd>{user.is_verified ? 'да' : 'нет'}</dd>
          </dl>
        )}

        <div className="row">
          <button type="button" className="btn-primary" onClick={handleLogout} disabled={busy}>
            Выйти
          </button>
          <button type="button" className="btn-secondary" onClick={() => void load()} disabled={busy}>
            Повторить /users/me
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={handleManualRefresh}
            disabled={busy}
          >
            Обновить токены
          </button>
        </div>

        <div className="tokens" key={tokenTick}>
          <h2>Токены в localStorage</h2>
          <p className="muted-note">
            Хранение в localStorage — упрощение учебного проекта; в продакшене безопаснее BFF
            с httpOnly-cookie.
          </p>
          <code>access: {preview(getAccessToken())}</code>
          <code>refresh: {preview(getRefreshToken())}</code>
        </div>
      </div>
    </div>
  )
}
