// ============= src/components/AuthForm/RegisterForm.tsx =============

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services/auth.service';
import { validators } from '../../utils/validators';
import { handleApiError } from '../../utils/errors';
import { ROUTES } from '../../utils/constants';
import { PasswordStrength } from '../PasswordStrength/PasswordStrength';
import './AuthForm.scss';

interface RegisterFormProps {
  onSuccess?: (userId: string, email: string) => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordConfirm: '',
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
    
    const usernameValidation = validators.username(formData.username);
    if (!usernameValidation.isValid) {
      newErrors.username = usernameValidation.error!;
    }
    
    const emailValidation = validators.email(formData.email);
    if (!emailValidation.isValid) {
      newErrors.email = emailValidation.error!;
    }
    
    const passwordValidation = validators.password(formData.password);
    if (!passwordValidation.isValid) {
      newErrors.password = passwordValidation.error!;
    }
    
    const passwordConfirmValidation = validators.passwordConfirm(
      formData.password,
      formData.passwordConfirm
    );
    if (!passwordConfirmValidation.isValid) {
      newErrors.passwordConfirm = passwordConfirmValidation.error!;
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
      const response = await authService.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.passwordConfirm,
      });
      
      if (response.requires_verification) {
        if (onSuccess) {
          onSuccess(response.user_id, response.email);
        } else {
          navigate(`${ROUTES.VERIFY_EMAIL}?user_id=${response.user_id}&email=${encodeURIComponent(response.email)}`);
        }
      } else {
        // Если верификация не требуется, переходим на страницу входа
        navigate(ROUTES.LOGIN);
      }
    } catch (error) {
      setGeneralError(handleApiError(error));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h1 className="auth-form__title">Регистрация</h1>
      
      {generalError && (
        <div className="auth-form__error">
          {generalError}
        </div>
      )}
      
      <div className="auth-form__field">
        <input
          type="text"
          placeholder="Имя пользователя"
          value={formData.username}
          onChange={(e) => handleChange('username', e.target.value)}
          className={`auth-form__input ${errors.username ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
          autoFocus
        />
        {errors.username && (
          <span className="auth-form__field-error">{errors.username}</span>
        )}
      </div>
      
      <div className="auth-form__field">
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          className={`auth-form__input ${errors.email ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
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
        {formData.password && <PasswordStrength password={formData.password} />}
        {errors.password && (
          <span className="auth-form__field-error">{errors.password}</span>
        )}
      </div>
      
      <div className="auth-form__field">
        <input
          type="password"
          placeholder="Повторите пароль"
          value={formData.passwordConfirm}
          onChange={(e) => handleChange('passwordConfirm', e.target.value)}
          className={`auth-form__input ${errors.passwordConfirm ? 'auth-form__input--error' : ''}`}
          disabled={isLoading}
        />
        {errors.passwordConfirm && (
          <span className="auth-form__field-error">{errors.passwordConfirm}</span>
        )}
      </div>
      
      <button
        type="submit"
        className="auth-form__submit"
        disabled={isLoading}
      >
        {isLoading ? (
          <span className="auth-form__submit-spinner" />
        ) : (
          'Зарегистрироваться'
        )}
      </button>
      
      <div className="auth-form__footer">
        <span>Уже есть аккаунт?</span>
        <Link to={ROUTES.LOGIN} className="auth-form__link">
          Войти
        </Link>
      </div>
    </form>
  );
};