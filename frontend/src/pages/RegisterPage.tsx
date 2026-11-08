import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../api/auth'
import { toMessage } from '../api/errors'
import { Alert } from '../components/Alert'
import { Field } from '../components/Field'

export function RegisterPage() {
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await register({ username, email, password })
      navigate('/login', {
        replace: true,
        state: { message: 'Регистрация прошла успешно — войдите с новым паролем' },
      })
    } catch (caught) {
      setError(toMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <div className="card">
        <h1>Регистрация</h1>
        <p className="subtitle">Требования ниже совпадают с валидацией на бэкенде</p>

        {error && <Alert kind="error">{error}</Alert>}

        <form onSubmit={handleSubmit}>
          <Field
            id="username"
            label="Имя пользователя"
            value={username}
            onChange={setUsername}
            autoComplete="username"
            hint="Не короче 3 символов"
          />
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
            autoComplete="new-password"
            hint={
              'Не короче 8 символов, минимум одна заглавная и одна строчная буква, ' +
              'одна цифра и один специальный символ (!@#$%^&*(),.?":{}|<>)'
            }
          />
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? 'Создаём аккаунт…' : 'Зарегистрироваться'}
          </button>
        </form>

        <p className="footer-link">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  )
}
