// src/pages/EmailVerificationPage.tsx

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Layout from "../components/Layout";
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
        <div className="id-badge">
            <div className="id-icon">
              <svg width="23" height="22" viewBox="0 0 23 22" xmlns="http://www.w3.org/2000/svg">
                <path d="M16.4131 19.3398L12.4463 13.0098L12.082 12.4287L11.6406 12.9531L7.85742 17.4482L7.73926 17.5879V20.9697H3.66211L4.19629 16.7354L9.09277 11.2275L9.51465 10.7539L8.95605 10.4541L5.6875 8.70312L5.65234 8.68359L5.61523 8.6709L2.07422 7.44922L21.7803 1.28809L16.4131 19.3398Z" fill="#69A2FF" stroke="#69A2FF"/>
              </svg>
            </div>
            <span className="id-text">ID</span>
          </div>

          <div className="logout-btn">
            <span className="material-symbols-outlined">close</span>
          </div>
            <div className="auth-content">
              <h1 className="auth-title emailverification-title">Подтвердите почту</h1>

              <div className="verification-block">
                
                <p className="verification-text">
                    Код отправлен на {emailParam || '—'}
                  </p>

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
    </Layout>
  );
};

export default EmailVerificationPage;
