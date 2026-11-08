import { ApiError, SessionExpiredError, formatDetail } from './errors'
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
  type TokenPair,
} from '../auth/tokens'

export const API_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/+$/, '')

type RequestOptions = {
  method?: 'GET' | 'POST'
  /** Тело запроса, сериализуется в JSON. */
  body?: unknown
  /** Подставлять ли `Authorization: Bearer <access_token>` и обновлять токены на 401. */
  auth?: boolean
}

/** Вызывается, когда сессия окончательно потеряна — App уводит на /login. */
let onSessionExpired: (() => void) | null = null

export function setSessionExpiredHandler(handler: (() => void) | null): void {
  onSessionExpired = handler
}

/**
 * Один «голый» запрос: без авторизационной логики и без повторов.
 * Разбирает и успешный ответ, и ошибку FastAPI в ApiError.
 */
async function rawRequest<T>(path: string, options: RequestOptions): Promise<T> {
  const { method = 'GET', body, auth = false } = options
  const headers: Record<string, string> = { Accept: 'application/json' }

  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth) {
    // Токен читается на каждой попытке, а не один раз снаружи:
    // повтор после refresh должен уйти уже с новым access-токеном.
    const accessToken = getAccessToken()
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`
  }

  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    // fetch падает только если запрос не дошёл: сервер не поднят, CORS, обрыв сети.
    throw new ApiError(
      0,
      null,
      `Не удалось связаться с API (${API_URL}). Проверьте, что бэкенд запущен.`,
    )
  }

  if (response.status === 204) return undefined as T

  const text = await response.text()
  let payload: unknown = null
  if (text) {
    try {
      payload = JSON.parse(text)
    } catch {
      payload = text
    }
  }

  if (!response.ok) {
    const detail =
      payload && typeof payload === 'object' && 'detail' in payload
        ? (payload as { detail: unknown }).detail
        : payload
    throw new ApiError(response.status, detail, formatDetail(detail, response.status))
  }

  return payload as T
}

/* ------------------------------------------------------------------ *
 * Обновление токенов: строго single-flight.
 *
 * На бэкенде ротация refresh-токенов с детекцией повторного использования
 * (src/services/user_service.py: refresh_tokens -> RefreshTokenReused ->
 * revoke_all_for_user). Два параллельных запроса с одним и тем же refresh
 * будут расценены как кража токена, и бэкенд отзовёт ВСЕ сессии пользователя.
 * Поэтому обновление в любой момент времени идёт ровно одно, а остальные
 * запросы ждут тот же Promise.
 * ------------------------------------------------------------------ */

let refreshPromise: Promise<TokenPair> | null = null

/**
 * Номер «поколения» токенов. Растёт при каждом завершённом обновлении.
 * Запрос, стартовавший до обновления, получит 401 с уже устаревшим access-токеном —
 * ему достаточно повторить попытку с новым токеном, а не крутить ещё одну ротацию.
 */
let tokenGeneration = 0

async function performRefresh(): Promise<TokenPair> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    clearTokens()
    tokenGeneration += 1
    onSessionExpired?.()
    throw new SessionExpiredError('Refresh-токена нет, войдите заново')
  }

  try {
    // Поле называется ровно refresh_token — см. RefreshTokenRequestDTO в src/dtos/auth.py.
    const pair = await rawRequest<TokenPair>('/users/refresh', {
      method: 'POST',
      body: { refresh_token: refreshToken },
    })
    setTokens(pair)
    tokenGeneration += 1
    return pair
  } catch (error) {
    clearTokens()
    tokenGeneration += 1
    onSessionExpired?.()
    const reason = error instanceof ApiError ? error.message : String(error)
    throw new SessionExpiredError(`Не удалось обновить токены: ${reason}`)
  }
}

function refreshOnce(): Promise<TokenPair> {
  if (refreshPromise) return refreshPromise

  const pending = performRefresh()
  refreshPromise = pending
  // Флаг снимаем только после settle, чтобы все ожидающие получили один результат.
  // Пустой catch — чтобы это служебное звено цепочки не считалось unhandled rejection.
  pending
    .catch(() => undefined)
    .finally(() => {
      if (refreshPromise === pending) refreshPromise = null
    })

  return pending
}

/** Обновить токены, если их уже не обновил кто-то другой параллельно. */
async function ensureFreshTokens(generationAtRequest: number): Promise<void> {
  if (tokenGeneration !== generationAtRequest) return
  await refreshOnce()
}

/** Сбросить состояние обновления (при logout/login — чтобы не тянуть старый Promise). */
export function resetRefreshState(): void {
  refreshPromise = null
  tokenGeneration += 1
}

/**
 * Основная обёртка над fetch.
 * Подставляет Authorization, разбирает ошибки, и при 401 ровно один раз
 * пробует обновить токены через /users/refresh и повторить исходный запрос.
 */
export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { auth = false } = options
  const generationAtRequest = tokenGeneration

  // Access-токена нет, а refresh есть: FastAPI HTTPBearer на запрос без заголовка
  // ответит 403, а не 401, и обработчик ниже не сработает. Обновляемся заранее.
  if (auth && !getAccessToken() && getRefreshToken()) {
    await ensureFreshTokens(generationAtRequest)
  }

  try {
    return await rawRequest<T>(path, options)
  } catch (error) {
    if (!auth || !(error instanceof ApiError) || error.status !== 401) throw error

    await ensureFreshTokens(generationAtRequest)
    return await rawRequest<T>(path, options)
  }
}
