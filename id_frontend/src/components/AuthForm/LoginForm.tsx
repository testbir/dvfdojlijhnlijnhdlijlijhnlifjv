// ============= src/components/AuthForm/LoginForm.tsx =============

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { validators } from '../../utils/validators';
import { handleApiError } from '../../utils/errors';
import { ROUTES } from '../../utils/constants';
import { useAuth } from '../../hooks/useAuth'

interface LoginFormProps {
  onSuccess?: () => void;
  redirectUrl?: string;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, redirectUrl }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');
  const { login } = useAuth();

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Очищаем ошибку поля при изменении
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
    if (generalError) {
      setGeneralError('');
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    const emailValidation = validators.email(formData.email);
    if (!emailValidation.isValid) {
      newErrors.email = emailValidation.error!;
    }
    
    const passwordValidation = validators.password(formData.password);
    if (!passwordValidation.isValid) {
      newErrors.password = passwordValidation.error!;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    setGeneralError('');
    
    try {
      await login(formData.email, formData.password)   // было: authService.login(formData)
      if (onSuccess) onSuccess()
      else if (redirectUrl) window.location.href = redirectUrl
      else window.location.href = ROUTES.PROFILE
    } catch (error) {
      setGeneralError(handleApiError(error))
    } finally {
      setIsLoading(false)
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h1 className="auth-form__title">Вход</h1>
      
      {generalError && (
        <div className="auth-form__error">
          {generalError}
        </div>
      )}
      
      <div className="auth-form__field">
        <input
          type="email"
          placeholder=" "
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          className={`auth-form__input ${errors.email ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
          autoFocus
        />
        <span className="auth-form__placeholder">Email</span>
        {errors.email && (
          <span className="auth-form__field-error">{errors.email}</span>
        )}
      </div>
      
      <div className="auth-form__field">
        <input
          type="password"
          placeholder=" "
          value={formData.password}
          onChange={(e) => handleChange('password', e.target.value)}
          className={`auth-form__input ${errors.password ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
        />
        <span className="auth-form__placeholder">Пароль</span>
        {errors.password && (
          <span className="auth-form__field-error">{errors.password}</span>
        )}
      </div>
      
      <div className="auth-form__links">
        <Link to={ROUTES.REGISTER} className="auth-form__link auth-form__link--register">
          Создать аккаунт
        </Link>
        <Link to={ROUTES.FORGOT_PASSWORD} className="auth-form__link auth-form__link--forgot">
          Забыли пароль?
        </Link>
      </div>
            
      <button
        type="submit"
        className="auth-form__submit"
        disabled={isLoading}
      >
        {isLoading ? (
          <span className="auth-form__submit-spinner" />
        ) : (
          'Войти'
        )}
      </button>
    
    </form>
  );
};
