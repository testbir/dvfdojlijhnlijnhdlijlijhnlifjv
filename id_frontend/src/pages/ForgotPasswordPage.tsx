// ============= src/pages/ForgotPasswordPage.tsx =============

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { authService } from '../services/auth.service';
import { validators } from '../utils/validators';
import { handleApiError } from '../utils/errors';
import { ROUTES } from '../utils/constants';
import '../styles/pages.scss';

export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validation = validators.email(email);
    if (!validation.isValid) {
      setError(validation.error!);
      return;
    }
    
    setError('');
    setIsLoading(true);
    
    try {
      await authService.forgotPassword({ email });
      setIsSuccess(true);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <Layout>
        <div className="forgot-page">
          <div className="forgot-page__success">
            <h2>Проверьте почту</h2>
            <p>Мы отправили инструкции по восстановлению пароля на {email}</p>
            <Link to={ROUTES.LOGIN} className="forgot-page__link">
              Вернуться к входу
            </Link>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="forgot-page">
        <h1 className="forgot-page__title">Восстановление пароля</h1>
        <p className="forgot-page__description">
          Введите email, указанный при регистрации
        </p>
        
        <form className="forgot-page__form" onSubmit={handleSubmit}>
          <input
            type="email"
            className={`forgot-page__input ${error ? 'forgot-page__input--error' : ''}`}
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
            autoFocus
          />
          
          {error && (
            <div className="forgot-page__error">
              {error}
            </div>
          )}
          
          <button
            type="submit"
            className="forgot-page__submit"
            disabled={isLoading}
          >
            {isLoading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>
        
        <Link to={ROUTES.LOGIN} className="forgot-page__link">
          Вернуться к входу
        </Link>
      </div>
    </Layout>
  );
};