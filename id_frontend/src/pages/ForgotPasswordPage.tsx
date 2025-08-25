// ============= src/pages/ForgotPasswordPage.tsx =============

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { CodeInput } from '../components/CodeInput/CodeInput';
import { authService } from '../services/auth.service';
import { validators, isWeakPassword } from '../utils/validators';
import { handleApiError } from '../utils/errors';
import { ROUTES, CODE_RESEND_TIMEOUT, CODE_LENGTH } from '../utils/constants';

function parseCooldownSeconds(msg: string): number | null {
  const m = msg.match(/Please wait (\d+) seconds/i);
  return m ? Number(m[1]) : null;
}

export const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();

  // step= "request" -> ввод email, "confirm" -> код + новый пароль
  const [step, setStep] = useState<'request' | 'confirm'>('request');

  // request
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // confirm
  const [code, setCode] = useState('');
  const [pwd, setPwd] = useState('');
  const [pwd2, setPwd2] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [weakPassword, setWeakPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // resend
  const [isResending, setIsResending] = useState(false);
  const [resendTimer, setResendTimer] = useState<number>(0);

  useEffect(() => {
    if (resendTimer <= 0) return;
    const id = setInterval(() => setResendTimer((s) => (s > 0 ? s - 1 : 0)), 1000);
    return () => clearInterval(id);
  }, [resendTimer]);

  const sendCode = async () => {
    const v = validators.email(email);
    if (!v.isValid) {
      setEmailError(v.error!);
      return;
    }
    setEmailError('');
    setIsLoading(true);
    try {
      await authService.forgotPassword({ email });
      setStep('confirm');
      setResendTimer(CODE_RESEND_TIMEOUT);
    } catch (err) {
      const msg = handleApiError(err);
      setEmailError(msg);
      const s = parseCooldownSeconds(msg);
      if (typeof s === 'number') setResendTimer(s);
    } finally {
      setIsLoading(false);
    }
  };

  const resend = async () => {
    if (resendTimer > 0 || !email) return;
    setIsResending(true);
    try {
      await authService.forgotPassword({ email });
      setResendTimer(CODE_RESEND_TIMEOUT);
      setCode('');
    } catch (err) {
      const msg = handleApiError(err);
      const s = parseCooldownSeconds(msg);
      if (typeof s === 'number') setResendTimer(s);
    } finally {
      setIsResending(false);
    }
  };

  const submitNewPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: Record<string, string> = {};

    const c = validators.code(code); if (!c.isValid) newErrors.code = c.error!;
    const p = validators.password(pwd); if (!p.isValid) newErrors.password = p.error!;
    const pc = validators.passwordConfirm(pwd, pwd2); if (!pc.isValid) newErrors.passwordConfirm = pc.error!;
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    if (isWeakPassword(pwd)) { setWeakPassword(true); return; }

    setIsSubmitting(true);
    try {
      await authService.resetPassword({
        email,
        code,
        new_password: pwd,
        new_password_confirm: pwd2,
      });
      navigate(ROUTES.LOGIN);
    } catch (err) {
      setErrors({ general: handleApiError(err) });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Layout>
      <div className="forgot-page">
        <h1 className="forgot-page__title">Сменить пароль</h1>

        {step === 'request' && (
          <>
            <p className="forgot-page__description">
              Введите email, указанный при регистрации
            </p>

            <form className="forgot-page__form" onSubmit={(e) => { e.preventDefault(); void sendCode(); }}>
              <input
                type="email"
                className={`forgot-page__input ${emailError ? 'forgot-page__input--error' : ''}`}
                placeholder="Email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setEmailError(''); }}
                disabled={isLoading}
                autoFocus
              />

              {emailError && <div className="forgot-page__error">{emailError}</div>}

              <Link to={ROUTES.LOGIN} className="auth-form__link auth-form__link--register">
                Вернуться к входу
              </Link>

              <button type="submit" className="forgot-page__submit" disabled={isLoading}>
                {isLoading ? 'Отправка...' : 'Отправить код'}
              </button>
            </form>
          </>
        )}

        {step === 'confirm' && (
          <>
            <p className="forgot-page__description">
              Мы отправили код на <b>{email}</b>. Введите код и новый пароль.
            </p>

            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16 }}>
              <CodeInput
                length={CODE_LENGTH}
                onChange={(val) => { setCode(val); if (errors.code) setErrors((e) => ({ ...e, code: '' })); }}
                error={!!errors.code}
                disabled={isSubmitting}
              />
            </div>
            {errors.code && <div className="forgot-page__error">{errors.code}</div>}

            <form className={`reset-page__form auth-form ${weakPassword ? 'auth-form--submitted' : ''}`} onSubmit={submitNewPassword}>
              <div className={`auth-form__field auth-form__field--password ${weakPassword ? 'is-weak' : ''}`}>
                <input
                  type="password"
                  placeholder=" "
                  value={pwd}
                  onChange={(e) => { setPwd(e.target.value); setWeakPassword(false); if (errors.password) setErrors((er) => ({ ...er, password: '' })); }}
                  className={`auth-form__input ${errors.password ? 'auth-form__input--error' : ''}`}
                  disabled={isSubmitting}
                />
                <span className="auth-form__placeholder">Новый пароль</span>
                {errors.password && <span className="auth-form__field-error">{errors.password}</span>}
              </div>

              <div className="auth-form__field">
                <input
                  type="password"
                  placeholder=" "
                  value={pwd2}
                  onChange={(e) => { setPwd2(e.target.value); if (errors.passwordConfirm) setErrors((er) => ({ ...er, passwordConfirm: '' })); }}
                  className={`auth-form__input ${errors.passwordConfirm ? 'auth-form__input--error' : ''}`}
                  disabled={isSubmitting}
                />
                <span className="auth-form__placeholder">Повторите пароль</span>
                {errors.passwordConfirm && <span className="auth-form__field-error">{errors.passwordConfirm}</span>}
              </div>

              {errors.general && (
                <div className="reset-page__error reset-page__error--general">{errors.general}</div>
              )}

              <button type="submit" className="auth-form__submit" disabled={isSubmitting || code.length !== CODE_LENGTH}>
                {isSubmitting ? 'Сохранение...' : 'Сменить пароль'}
              </button>
            </form>

            <div className="verify-page__resend" style={{ marginTop: 16, textAlign: 'center' }}>
              {resendTimer > 0 ? (
                <span className="verify-page__timer">
                  Отправить код повторно через {resendTimer}с
                </span>
              ) : (
                <button
                  className="verify-page__resend-btn"
                  onClick={() => { void resend(); }}
                  disabled={isResending}
                >
                  {isResending ? 'Отправка...' : 'Отправить код повторно'}
                </button>
              )}
            </div>

            <div style={{ textAlign: 'center', marginTop: 16 }}>
              <button
                className="verify-page__resend-btn"
                onClick={() => setStep('request')}
                disabled={isSubmitting || isResending}
              >
                Изменить email
              </button>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
};
