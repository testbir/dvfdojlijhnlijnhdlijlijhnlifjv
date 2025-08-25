// ============= src/pages/ResetPasswordPage.tsx =============
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { authService } from '../services/auth.service';
import { validators, isWeakPassword } from '../utils/validators';
import { handleApiError } from '../utils/errors';
import { ROUTES } from '../utils/constants';

export const ResetPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const userId = searchParams.get('user_id');
  const code = searchParams.get('code');

  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [weakPassword, setWeakPassword] = useState(false);

  useEffect(() => {
    if (!userId || !code) navigate(ROUTES.FORGOT_PASSWORD);
  }, [userId, code, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);

    const newErrors: Record<string, string> = {};
    const p = validators.password(password); if (!p.isValid) newErrors.password = p.error!;
    const pc = validators.passwordConfirm(password, passwordConfirm); if (!pc.isValid) newErrors.passwordConfirm = pc.error!;
    if (Object.keys(newErrors).length > 0) { setErrors(newErrors); return; }

    if (isWeakPassword(password)) { setWeakPassword(true); return; }
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

        <form className={`reset-page__form auth-form ${submitted ? 'auth-form--submitted' : ''}`} onSubmit={handleSubmit}>
          <div className={`reset-page__field auth-form__field auth-form__field--password ${weakPassword ? 'is-weak' : ''}`}>
            <input
              type="password"
              className={`reset-page__input auth-form__input ${errors.password ? 'reset-page__input--error auth-form__input--error' : ''}`}
              placeholder="Новый пароль"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setWeakPassword(false); }}
              disabled={isLoading}
              autoFocus
            />
            {errors.password && <span className="reset-page__error">{errors.password}</span>}
          </div>

          <div className="reset-page__field auth-form__field">
            <input
              type="password"
              className={`reset-page__input auth-form__input ${errors.passwordConfirm ? 'reset-page__input--error auth-form__input--error' : ''}`}
              placeholder="Повторите пароль"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              disabled={isLoading}
            />
            {errors.passwordConfirm && <span className="reset-page__error">{errors.passwordConfirm}</span>}
          </div>

          {errors.general && <div className="reset-page__error reset-page__error--general">{errors.general}</div>}

          <button type="submit" className="reset-page__submit auth-form__submit" disabled={isLoading}>
            {isLoading ? 'Сохранение...' : 'Сохранить пароль'}
          </button>
        </form>
      </div>
    </Layout>
  );
};
