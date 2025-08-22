// ============= src/components/AuthForm/LoginForm.tsx =============

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../../services/auth.service';
import { validators } from '../../utils/validators';
import { handleApiError } from '../../utils/errors';
import { ROUTES } from '../../utils/constants';
import './AuthForm.scss';

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
      await authService.login(formData);
      
      if (onSuccess) {
        onSuccess();
      } else if (redirectUrl) {
        window.location.href = redirectUrl;
      } else {
        window.location.href = ROUTES.PROFILE;
      }
    } catch (error) {
      setGeneralError(handleApiError(error));
    } finally {
      setIsLoading(false);
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
          placeholder="Email"
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          className={`auth-form__input ${errors.email ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
          autoFocus
        />
        {errors.email && (
          <span className="auth-form__field-error">{errors.email}</span>
        )}
      </div>
      
      <div className="auth-form__field">
        <input
          type="password"
          placeholder="Пароль"
          value={formData.password}
          onChange={(e) => handleChange('password', e.target.value)}
          className={`auth-form__input ${errors.password ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
        />
        {errors.password && (
          <span className="auth-form__field-error">{errors.password}</span>
        )}
      </div>
      
      <Link to={ROUTES.FORGOT_PASSWORD} className="auth-form__link">
        Забыли пароль?
      </Link>
      
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
      
      <div className="auth-form__footer">
        <span>Нет аккаунта?</span>
        <Link to={ROUTES.REGISTER} className="auth-form__link">
          Зарегистрироваться
        </Link>
      </div>
    </form>
  );
};