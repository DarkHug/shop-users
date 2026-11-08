/**
 * Хранение токенов.
 *
 * УПРОЩЕНИЕ ДЛЯ УЧЕБНОГО ПРОЕКТА: пара access/refresh лежит в localStorage.
 * localStorage читается любым JS на странице, поэтому при XSS токены утекают
 * целиком (включая долгоживущий refresh). В продакшене безопаснее схема BFF:
 * токены живут на сервере-посреднике, а в браузер уходит только httpOnly +
 * Secure + SameSite cookie, недоступная из JS, плюс CSRF-защита на мутациях.
 * Здесь localStorage выбран сознательно — чтобы руками прогонять сценарии
 * авторизации и видеть токены в DevTools.
 */

export type TokenPair = {
  access_token: string
  refresh_token: string
}

const ACCESS_KEY = 'prosto_shop.access_token'
const REFRESH_KEY = 'prosto_shop.refresh_token'

type Listener = () => void
const listeners = new Set<Listener>()

/** Подписка для UI: вызывается на любое изменение токенов в этой вкладке. */
export function subscribeTokens(listener: Listener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

function notify(): void {
  for (const listener of listeners) listener()
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY)
}

export function setTokens(pair: TokenPair): void {
  localStorage.setItem(ACCESS_KEY, pair.access_token)
  localStorage.setItem(REFRESH_KEY, pair.refresh_token)
  notify()
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  notify()
}

/** Есть ли вообще чем авторизоваться (хватит любого из двух токенов). */
export function hasTokens(): boolean {
  return Boolean(getAccessToken() || getRefreshToken())
}
