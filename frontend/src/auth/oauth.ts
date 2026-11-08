import type { OAuthProvider } from '../api/auth'

/**
 * state для OAuth.
 *
 * Бэкенд не отдаёт state отдельным полем — он лежит внутри ссылки, которую
 * вернул GET /auth/<provider>/url. Достаём его из query-параметров и держим
 * в sessionStorage (своим ключом на провайдера), чтобы на странице callback
 * сверить с тем, что пришло от провайдера. Это защита от login CSRF:
 * без сверки злоумышленник может подсунуть свой code и залогинить жертву
 * в свой аккаунт. Если state не совпал или его нет — запрос на бэкенд
 * не отправляем вообще.
 *
 * sessionStorage, а не localStorage: state живёт один вход и не должен
 * переживать закрытие вкладки.
 */

function storageKey(provider: OAuthProvider): string {
  return `prosto_shop.oauth_state.${provider}`
}

/** Вытащить state из ссылки авторизации провайдера. */
export function extractState(authorizationUrl: string): string | null {
  try {
    return new URL(authorizationUrl).searchParams.get('state')
  } catch {
    return null
  }
}

export function saveState(provider: OAuthProvider, state: string): void {
  sessionStorage.setItem(storageKey(provider), state)
}

/** Прочитать и сразу удалить сохранённый state (одноразовый по смыслу). */
export function takeState(provider: OAuthProvider): string | null {
  const key = storageKey(provider)
  const state = sessionStorage.getItem(key)
  sessionStorage.removeItem(key)
  return state
}
