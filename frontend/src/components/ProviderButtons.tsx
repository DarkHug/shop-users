import { useState } from 'react'
import { getOAuthUrl, type OAuthProvider } from '../api/auth'
import { ApiError, toMessage } from '../api/errors'
import { extractState, saveState } from '../auth/oauth'

const LABELS: Record<OAuthProvider, string> = {
  google: 'Войти через Google',
  github: 'Войти через GitHub',
}

/** Бэкенд GitHub-провайдера ещё в разработке: роутер может быть не подключён. */
const NOT_IMPLEMENTED_MESSAGE = 'GitHub-вход пока недоступен'

type Props = {
  onError: (message: string) => void
}

export function ProviderButtons({ onError }: Props) {
  const [pending, setPending] = useState<OAuthProvider | null>(null)

  async function start(provider: OAuthProvider) {
    setPending(provider)
    onError('')
    try {
      const authorizationUrl = await getOAuthUrl(provider)

      // state приходит внутри ссылки, отдельным полем бэкенд его не отдаёт.
      const state = extractState(authorizationUrl)
      if (!state) {
        onError(`Бэкенд вернул ссылку без параметра state — вход через ${provider} невозможен`)
        setPending(null)
        return
      }
      saveState(provider, state)

      window.location.href = authorizationUrl
    } catch (error) {
      const notImplemented =
        provider === 'github' &&
        error instanceof ApiError &&
        (error.status === 404 || error.status === 405 || error.isNetworkError)

      onError(notImplemented ? NOT_IMPLEMENTED_MESSAGE : toMessage(error))
      setPending(null)
    }
  }

  return (
    <div className="providers">
      {(Object.keys(LABELS) as OAuthProvider[]).map((provider) => (
        <button
          key={provider}
          type="button"
          className="btn-secondary"
          disabled={pending !== null}
          onClick={() => start(provider)}
        >
          {pending === provider ? 'Переходим к провайдеру…' : LABELS[provider]}
        </button>
      ))}
    </div>
  )
}
