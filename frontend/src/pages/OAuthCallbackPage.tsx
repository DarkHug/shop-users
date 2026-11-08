import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { oauthCallback, type OAuthProvider } from '../api/auth'
import { ApiError, toMessage } from '../api/errors'
import { Alert } from '../components/Alert'
import { takeState } from '../auth/oauth'

const PROVIDER_NAMES: Record<OAuthProvider, string> = {
  google: 'Google',
  github: 'GitHub',
}

function describeFailure(provider: OAuthProvider, error: unknown): string {
  const name = PROVIDER_NAMES[provider]

  if (error instanceof ApiError) {
    if (provider === 'github' && (error.status === 404 || error.status === 405 || error.isNetworkError)) {
      return 'GitHub-вход пока недоступен'
    }
    switch (error.status) {
      case 400:
        return `Сессия входа истекла или недействительна (${error.message}). Начните вход заново.`
      case 403:
        return `Почта в аккаунте ${name} не подтверждена — войти через него нельзя.`
      case 503:
        return `${name} временно недоступен, попробуйте позже.`
      default:
        return error.message
    }
  }

  return toMessage(error)
}

type Props = {
  provider: OAuthProvider
}

export function OAuthCallbackPage({ provider }: Props) {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [error, setError] = useState('')

  /**
   * React StrictMode в dev-режиме монтирует компонент и прогоняет эффекты дважды.
   * state на бэкенде одноразовый (Redis GETDEL в OAuthStateRepository), поэтому
   * второй POST /auth/<provider>/callback получит 400 и затрёт уже успешный вход.
   * Флаг в ref живёт между повторными вызовами эффекта и гарантирует ровно один
   * запрос — при этом StrictMode глобально не отключён.
   */
  const startedRef = useRef(false)

  useEffect(() => {
    if (startedRef.current) return
    startedRef.current = true

    const code = searchParams.get('code')
    const state = searchParams.get('state')
    const providerError = searchParams.get('error')
    const providerErrorDescription = searchParams.get('error_description')

    // Сохранённый state забираем (и удаляем) при любом сценарии: он одноразовый,
    // и оставлять его в sessionStorage после неудачной попытки нельзя.
    const savedState = takeState(provider)

    if (providerError) {
      setError(
        `Вход через ${PROVIDER_NAMES[provider]} не завершён: ${providerErrorDescription ?? providerError}`,
      )
      return
    }

    if (!code || !state) {
      setError('Провайдер не передал code или state — запрос на бэкенд не отправлен')
      return
    }

    // Главная проверка: без совпадения state запрос на бэкенд не уходит вообще.
    // Иначе чужой code мог бы залогинить пользователя в подставной аккаунт (login CSRF).
    if (!savedState) {
      setError(
        'Не найден сохранённый state этой попытки входа — запрос на бэкенд не отправлен. ' +
          'Начните вход заново со страницы входа.',
      )
      return
    }

    if (savedState !== state) {
      setError(
        'state из ответа провайдера не совпал с сохранённым — запрос на бэкенд не отправлен ' +
          '(защита от login CSRF).',
      )
      return
    }

    oauthCallback(provider, code, state)
      .then(() => navigate('/me', { replace: true }))
      .catch((caught) => setError(describeFailure(provider, caught)))
  }, [provider, searchParams, navigate])

  return (
    <div className="page">
      <div className="card">
        <h1>Вход через {PROVIDER_NAMES[provider]}</h1>

        {error ? (
          <>
            <Alert kind="error">{error}</Alert>
            <p className="footer-link">
              <Link to="/login">Вернуться на страницу входа</Link>
            </p>
          </>
        ) : (
          <Alert kind="info">Завершаем вход, обмениваем код на токены…</Alert>
        )}
      </div>
    </div>
  )
}
