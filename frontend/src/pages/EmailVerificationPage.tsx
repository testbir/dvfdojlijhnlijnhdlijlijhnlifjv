// src/pages/EmailVerificationPage.tsx

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Layout from "../components/Layout";
import authlogo from "../assets/authlogo.png";
import logomobile from "../assets/logomobile.png";
import CodeInput from '../components/CodeInput';
import authService from '../services/authService';

import "../styles/auth.scss";
import "../styles/EmailVerificationPage.scss";

const EmailVerificationPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const purpose = searchParams.get('purpose'); // 'register' | 'reset_password'
  const userIdParam = searchParams.get('user_id');
  const emailParam = searchParams.get('email');

  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [timer, setTimer] = useState(60);
  const [resending, setResending] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimer(prev => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Валидация входных параметров
  useEffect(() => {
    if (purpose === 'reset_password' && !emailParam) {
      navigate('/forgot-password');
      return;
    }
    if (purpose === 'register' && !userIdParam) {
      navigate('/register');
      return;
    }
    if (purpose !== 'register' && purpose !== 'reset_password') {
      navigate('/login');
    }
  }, [purpose, userIdParam, emailParam, navigate]);

  const handleVerify = async () => {
    setError('');
    try {
      if (purpose === 'register') {
        // вернёт и сохранит токены
        await authService.verifyCode(Number(userIdParam), code);
        navigate('/?message=activated');
      } else if (purpose === 'reset_password') {
        const res = await authService.verifyResetCode(String(emailParam), code);
        navigate(`/set-new-password?user_id=${res.user_id}`);
      }
    } catch (err: any) {
      setError(err?.response?.data?.error || err?.message || 'Ошибка проверки кода');
    }
  };

  const handleResend = async () => {
    if (timer > 0 || resending) return;
    setResending(true);
    setError('');

    try {
      if (purpose === 'register') {
        if (!userIdParam) throw new Error('Отсутствует user_id');
        await authService.resendCode(Number(userIdParam), 'register');
      } else if (purpose === 'reset_password') {
        if (!emailParam) throw new Error('Отсутствует email');
        await authService.requestPasswordReset(String(emailParam));
      }
      setTimer(60);
    } catch (err: any) {
      setError(err?.response?.data?.error || err?.message || 'Не удалось отправить код повторно');
    } finally {
      setResending(false);
    }
  };

  return (
    <Layout>
      <div className="auth-wrapper email-verification-page">
        <div className="auth-box">
          <div className="auth-side auth-side--left">
            <div className="auth-logo-container">
              <div className="auth-logo">
                <img src={authlogo} alt="AsyncTeach" />
              </div>
            </div>
          </div>

          <div className="auth-side auth-side--right">
            <div className="mobile-logo-container mobile-logo-container--center">
              <div className="mobile-logo">
                <img src={logomobile} alt="AsyncTeach" />
              </div>
            </div>

            <div className="auth-content">
              <h1 className="auth-title emailverification-title">Подтвердите почту</h1>

              <div className="verification-block">
                <p className="verification-text">Мы отправили код на твою почту</p>

                <CodeInput length={4} onComplete={setCode} />

                <div className="resend-block">
                  {timer > 0 ? (
                    <p className="resend-timer">Можно запросить повторно через {timer} сек.</p>
                  ) : (
                    <button
                      onClick={handleResend}
                      disabled={resending}
                      className="resend-text"
                    >
                      {resending ? 'Отправляем...' : 'Повторно отправить код'}
                    </button>
                  )}
                </div>
              </div>

              <div className="auth-error-container"></div>
              {error && <div className="auth-error emailverification-error">{error}</div>}

              <button
                onClick={handleVerify}
                disabled={code.length !== 4}
                className="auth-button emailverification-button"
              >
                Подтвердить
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default EmailVerificationPage;
