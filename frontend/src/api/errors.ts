/**
 * Ошибки FastAPI всегда приходят в поле `detail`, но в двух разных формах:
 *  - строка: `{"detail": "Invalid credentials"}` — ручные HTTPException в роутерах;
 *  - массив объектов валидации (422): `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`.
 * ApiError хранит сырой detail, а человекочитаемый текст собирает formatDetail.
 */

export type ValidationItem = {
  loc?: (string | number)[]
  msg?: string
  type?: string
}

export type ApiErrorDetail = string | ValidationItem[] | unknown

export class ApiError extends Error {
  /** HTTP-статус; 0 — запрос вообще не дошёл до сервера (сеть/CORS). */
  readonly status: number
  readonly detail: ApiErrorDetail

  constructor(status: number, detail: ApiErrorDetail, message?: string) {
    super(message ?? formatDetail(detail, status))
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }

  get isNetworkError(): boolean {
    return this.status === 0
  }
}

/** Сессия протухла окончательно: refresh не сработал, токены вычищены. */
export class SessionExpiredError extends Error {
  constructor(message = 'Сессия истекла, войдите заново') {
    super(message)
    this.name = 'SessionExpiredError'
  }
}

function isValidationItemArray(value: unknown): value is ValidationItem[] {
  return (
    Array.isArray(value) &&
    value.every((item) => typeof item === 'object' && item !== null)
  )
}

function formatValidationItem(item: ValidationItem): string {
  // loc выглядит как ["body", "password"] — берём последний осмысленный сегмент.
  const field = (item.loc ?? [])
    .filter((part) => part !== 'body' && part !== 'query' && part !== 'path')
    .join('.')
  // Pydantic добавляет префикс "Value error, " к сообщениям кастомных валидаторов.
  const msg = (item.msg ?? 'некорректное значение').replace(/^Value error,\s*/i, '')
  return field ? `${field}: ${msg}` : msg
}

const STATUS_FALLBACKS: Record<number, string> = {
  400: 'Сессия входа истекла или недействительна. Попробуйте войти снова',
  401: 'Неверные данные или истёкший токен',
  403: 'Доступ запрещён',
  404: 'Не найдено',
  409: 'Такой пользователь уже существует',
  422: 'Данные не прошли валидацию',
  500: 'Внутренняя ошибка сервера',
  503: 'Сервис провайдера временно недоступен, попробуйте позже',
}

export function formatDetail(detail: ApiErrorDetail, status = 0): string {
  if (typeof detail === 'string' && detail.trim()) return detail
  if (isValidationItemArray(detail) && detail.length > 0) {
    return detail.map(formatValidationItem).join('; ')
  }
  if (detail && typeof detail === 'object') {
    try {
      return JSON.stringify(detail)
    } catch {
      /* падать из-за форматирования ошибки — худший из вариантов */
    }
  }
  return STATUS_FALLBACKS[status] ?? `Ошибка запроса (HTTP ${status || 'нет ответа'})`
}

/** Текст для показа пользователю из любого брошенного значения. */
export function toMessage(error: unknown): string {
  if (error instanceof ApiError || error instanceof SessionExpiredError) return error.message
  if (error instanceof Error) return error.message
  return String(error)
}
