// src/pages/EmailVerificationPage.tsx

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { createApi } from '../api/axiosInstance';
const axiosInstance = createApi('/auth-api');
import Layout from "../components/Layout";
import authlogo from "../assets/authlogo.png";
import logomobile from "../assets/logomobile.png"; // Импорт мобильного логотипа
import CodeInput from '../components/CodeInput';

// Стили
import "../styles/auth.scss"
import "../styles/EmailVerificationPage.scss"

const EmailVerificationPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const userId = searchParams.get('user_id');
  const purpose = searchParams.get('purpose'); // 'register' | 'reset_password'
  const navigate = useNavigate();

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

  useEffect(() => {
    // Проверка обязательных параметров при загрузке
    if (purpose === 'reset_password' && !searchParams.get('email')) {
      navigate('/forgot-password');
      return;
    }
    if (purpose === 'register' && !userId) {
      navigate('/register');
      return;
    }
  }, [purpose, userId, searchParams, navigate]);

  const handleVerify = async () => {
    setError('');

    try {
      if (purpose === 'register') {
        await axiosInstance.post('/api/verify-code/', {
          user_id: Number(userId),
          code,
        });

        // После активации регистрации - сразу на главную с уведомлением
        navigate('/?message=activated');
        
      } else if (purpose === 'reset_password') {
        const response = await axiosInstance.post('/api/verify-reset-code/', {
          email: searchParams.get('email'),
          code,
        });
        const userIdFromReset = response.data.user_id;
        navigate(`/set-new-password?user_id=${userIdFromReset}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка проверки кода');
    }
  };

  const handleResend = async () => {
    if (timer > 0 || resending) return;
    setResending(true);
    setError('');

    // Валидация входных данных
    if (purpose === 'register' && !userId) {
      setError('Отсутствует user_id');
      setResending(false);
      return;
    }

    if (purpose === 'reset_password' && !searchParams.get('email')) {
      setError('Отсутствует email');
      setResending(false);
      return;
    }

    try {
      if (purpose === 'register') {
        await axiosInstance.post('/api/resend-code/', {
          user_id: Number(userId),
          purpose: 'register',
        });
      } else if (purpose === 'reset_password') {
        await axiosInstance.post('/api/request-reset/', {
          email: searchParams.get('email'),
        });
      }

      setTimer(60);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Не удалось отправить код повторно');
    } finally {
      setResending(false);
    }
  };

  return (
    <Layout>
      <div className="auth-wrapper email-verification-page">
        <div className="auth-box">
          {/* Левая сторона (логотип) - показывается только на десктопе */}
          <div className="auth-side auth-side--left">
            {/* Контейнер логотипа — по центру блока */}
            <div className="auth-logo-container">
              <div className="auth-logo">
                <img src={authlogo} alt="AsyncTeach" />
              </div>
            </div>
          </div>

          {/* Правая сторона (форма подтверждения) */}
          <div className="auth-side auth-side--right">
            
            {/* Мобильный логотип - только логотип без кнопки назад */}
            <div className="mobile-logo-container mobile-logo-container--center">
              <div className="mobile-logo">
                <img src={logomobile} alt="AsyncTeach" />
              </div>
            </div>

            <div className="auth-content">
              <h1 className="auth-title emailverification-title">Подтвердите почту</h1>

              {/* Блок с подтверждением */}
              <div className="verification-block">
                <p className="verification-text">Мы отправили код на твою почту</p>
                
                {/* 4 прямоугольника для кода */}
                <CodeInput length={4} onComplete={setCode} />
                
                {/* Повторная отправка */}
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

              {/* Блок с ошибкой */}
              <div className="auth-error-container"></div>
              {error && <div className="auth-error emailverification-error">{error}</div>}

              {/* Кнопка подтверждения */}
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