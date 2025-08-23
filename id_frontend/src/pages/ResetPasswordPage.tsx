// ============= src/pages/ResetPasswordPage.tsx =============

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { PasswordStrength } from '../components/PasswordStrength/PasswordStrength';
import { authService } from '../services/auth.service';
import { validators } from '../utils/validators';
import { handleApiError } from '../utils/errors';
import { ROUTES } from '../utils/constants';
import '../styles/pages.scss';

export const ResetPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const userId = searchParams.get('user_id');
  const code = searchParams.get('code');
  
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!userId || !code) {
      navigate(ROUTES.FORGOT_PASSWORD);
    }
  }, [userId, code, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors: Record<string, string> = {};
    
    const passwordValidation = validators.password(password);
    if (!passwordValidation.isValid) {
      newErrors.password = passwordValidation.error!;
    }
    
    const confirmValidation = validators.passwordConfirm(password, passwordConfirm);
    if (!confirmValidation.isValid) {
      newErrors.passwordConfirm = confirmValidation.error!;
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    if (!userId || !code) return;
    
    setIsLoading(true);
    setErrors({});
    
    try {
      await authService.resetPassword({
        user_id: userId,
        code,
        new_password: password,
        new_password_confirm: passwordConfirm,
      });
      navigate(ROUTES.LOGIN);
    } catch (err) {
      setErrors({ general: handleApiError(err) });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="reset-page">
        <h1 className="reset-page__title">Новый пароль</h1>
        
        <form className="reset-page__form" onSubmit={handleSubmit}>
          <div className="reset-page__field">
            <input
              type="password"
              className={`reset-page__input ${errors.password ? 'reset-page__input--error' : ''}`}
              placeholder="Новый пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              autoFocus
            />
            {password && <PasswordStrength password={password} />}
            {errors.password && (
              <span className="reset-page__error">{errors.password}</span>
            )}
          </div>
          
          <div className="reset-page__field">
            <input
              type="password"
              className={`reset-page__input ${errors.passwordConfirm ? 'reset-page__input--error' : ''}`}
              placeholder="Повторите пароль"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              disabled={isLoading}
            />
            {errors.passwordConfirm && (
              <span className="reset-page__error">{errors.passwordConfirm}</span>
            )}
          </div>
          
          {errors.general && (
            <div className="reset-page__error reset-page__error--general">
              {errors.general}
            </div>
          )}
          
          <button
            type="submit"
            className="reset-page__submit"
            disabled={isLoading}
          >
            {isLoading ? 'Сохранение...' : 'Сохранить пароль'}
          </button>
        </form>
      </div>
    </Layout>
  );
};