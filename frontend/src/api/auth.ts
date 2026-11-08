import { apiRequest, resetRefreshState } from './client'
import { clearTokens, getRefreshToken, setTokens, type TokenPair } from '../auth/tokens'

/** Ответ GET /users/me — UserReadDTO из src/dtos/users.py. */
export type User = {
  id: string
  /** nullable в БД: у пользователей, созданных через OAuth, username отсутствует. */
  username: string | null
  email: string
  is_verified: boolean
}

export type OAuthProvider = 'google' | 'github'

export type RegisterPayload = {
  username: string
  email: string
  password: string
}

/** POST /users/ — 201 без тела; 409 если email/username заняты; 422 на валидации. */
export async function register(payload: RegisterPayload): Promise<void> {
  await apiRequest<void>('/users/', { method: 'POST', body: payload })
}

/** POST /users/login — 200 с парой токенов; 401 при неверных данных. */
export async function login(email: string, password: string): Promise<TokenPair> {
  const pair = await apiRequest<TokenPair>('/users/login', {
    method: 'POST',
    body: { email, password },
  })
  resetRefreshState()
  setTokens(pair)
  return pair
}

/** GET /users/me — требует Authorization: Bearer <access_token>. */
export async function getMe(): Promise<User> {
  return apiRequest<User>('/users/me', { auth: true })
}

/** GET /auth/<provider>/url — ответ {url} со state внутри query-параметров. */
export async function getOAuthUrl(provider: OAuthProvider): Promise<string> {
  const { url } = await apiRequest<{ url: string }>(`/auth/${provider}/url`)
  return url
}

/** POST /auth/<provider>/callback — обмен code+state на пару токенов. */
export async function oauthCallback(
  provider: OAuthProvider,
  code: string,
  state: string,
): Promise<TokenPair> {
  const pair = await apiRequest<TokenPair>(`/auth/${provider}/callback`, {
    method: 'POST',
    body: { code, state },
  })
  resetRefreshState()
  setTokens(pair)
  return pair
}

/**
 * POST /users/logout — 204 при успехе, 404 если токен уже неизвестен бэкенду.
 * Токены на клиенте чистим независимо от результата: локальный выход
 * не должен зависеть от того, доступен ли сервер.
 */
export async function logout(): Promise<void> {
  const refreshToken = getRefreshToken()
  try {
    if (refreshToken) {
      await apiRequest<void>('/users/logout', {
        method: 'POST',
        body: { refresh_token: refreshToken },
      })
    }
  } finally {
    clearTokens()
    resetRefreshState()
  }
}

/** Ручное обновление пары токенов — для прогонки сценария из UI. */
export async function refreshTokensManually(): Promise<TokenPair> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) throw new Error('Refresh-токена нет')
  const pair = await apiRequest<TokenPair>('/users/refresh', {
    method: 'POST',
    body: { refresh_token: refreshToken },
  })
  resetRefreshState()
  setTokens(pair)
  return pair
}
