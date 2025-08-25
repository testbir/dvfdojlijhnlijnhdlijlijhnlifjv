/* ============= src/components/AuthForm/RegisterForm.tsx ============= */

import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '../../services/auth.service'
import { validators, isWeakPassword } from '../../utils/validators'
import { handleApiError } from '../../utils/errors'
import { ROUTES } from '../../utils/constants'

interface RegisterFormProps {
  onSuccess?: (userId: string, email: string) => void
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordConfirm: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [generalError, setGeneralError] = useState('')
  const [weakPassword, setWeakPassword] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: '' }))
    if (generalError) setGeneralError('')
    if (field === 'password') setWeakPassword(false)
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    const u = validators.username(formData.username); if (!u.isValid) newErrors.username = u.error!
    const e = validators.email(formData.email); if (!e.isValid) newErrors.email = e.error!
    const p = validators.password(formData.password); if (!p.isValid) newErrors.password = p.error!
    const pc = validators.passwordConfirm(formData.password, formData.passwordConfirm); if (!pc.isValid) newErrors.passwordConfirm = pc.error!
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)

    if (!validateForm()) return
    if (isWeakPassword(formData.password)) { setWeakPassword(true); return }

    setIsLoading(true)
    setGeneralError('')

    try {
      const r = await authService.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.passwordConfirm,
      })

      if (r.requires_verification) {
        const url = `${ROUTES.VERIFY_EMAIL}?user_id=${r.user_id}&email=${encodeURIComponent(r.email)}`
        onSuccess ? onSuccess(r.user_id, r.email) : navigate(url)
      } else {
        navigate(ROUTES.LOGIN)
      }
    } catch (error) {
      setGeneralError(handleApiError(error))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form className={`auth-form ${submitted ? 'auth-form--submitted' : ''}`} onSubmit={handleSubmit}>
      <h1 className="auth-form__title">Регистрация</h1>

      {generalError && <div className="auth-form__error">{generalError}</div>}

      <div className="auth-form__field">
        <input
          type="text"
          placeholder=" "
          value={formData.username}
          onChange={(e) => handleChange('username', e.target.value)}
          className={`auth-form__input ${errors.username ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
          autoFocus
        />
        <span className="auth-form__placeholder">Имя пользователя</span>
        {errors.username && <span className="auth-form__field-error">{errors.username}</span>}
      </div>

      <div className="auth-form__field">
        <input
          type="email"
          placeholder=" "
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          className={`auth-form__input ${errors.email ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
        />
        <span className="auth-form__placeholder">Email</span>
        {errors.email && <span className="auth-form__field-error">{errors.email}</span>}
      </div>

      <div className={`auth-form__field auth-form__field--password ${weakPassword ? 'is-weak' : ''}`}>
        <input
          type="password"
          placeholder=" "
          value={formData.password}
          onChange={(e) => handleChange('password', e.target.value)}
          className={`auth-form__input ${errors.password ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
        />
        <span className="auth-form__placeholder">Пароль</span>
        {errors.password && <span className="auth-form__field-error">{errors.password}</span>}
      </div>

      <div className="auth-form__field">
        <input
          type="password"
          placeholder=" "
          value={formData.passwordConfirm}
          onChange={(e) => handleChange('passwordConfirm', e.target.value)}
          className={`auth-form__input ${errors.passwordConfirm ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
        />
        <span className="auth-form__placeholder">Повторите пароль</span>
        {errors.passwordConfirm && <span className="auth-form__field-error">{errors.passwordConfirm}</span>}
      </div>

      <div className="auth-form__links">
        <Link to={ROUTES.LOGIN} className="auth-form__link auth-form__link--register">Войти в аккаунт</Link>
      </div>

      <button type="submit" className="auth-form__submit" disabled={isLoading}>
        {isLoading ? <span className="auth-form__submit-spinner" /> : 'Зарегистрироваться'}
      </button>
    </form>
  )
}
