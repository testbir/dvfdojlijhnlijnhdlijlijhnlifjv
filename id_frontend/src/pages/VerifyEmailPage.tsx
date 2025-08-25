// ============= src/pages/VerifyEmailPage.tsx =============

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { CodeInput } from '../components/CodeInput/CodeInput';
import { LoadingOverlay } from '../components/LoadingOverlay/LoadingOverlay';
import { authService } from '../services/auth.service';
import { handleApiError } from '../utils/errors';
import { ROUTES, CODE_RESEND_TIMEOUT, CODE_LENGTH } from '../utils/constants';

export const VerifyEmailPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const userId = searchParams.get('user_id');
  const email = searchParams.get('email');
  
  const [, setCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [resendTimer, setResendTimer] = useState(CODE_RESEND_TIMEOUT);

  useEffect(() => {
    if (!userId || !email) {
      navigate(ROUTES.REGISTER);
    }
  }, [userId, email, navigate]);

  useEffect(() => {
    const timer = setInterval(() => {
      setResendTimer((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleVerify = async (verificationCode: string) => {
    if (!userId) return;
    
    setError('');
    setIsLoading(true);
    
    try {
      await authService.verifyEmail({
        user_id: userId,
        code: verificationCode,
      });
      navigate(ROUTES.PROFILE);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (!userId || resendTimer > 0) return;
    
    setIsResending(true);
    setError('');
    
    try {
      await authService.resendVerificationCode(userId);
      setResendTimer(CODE_RESEND_TIMEOUT);
      setCode('');
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsResending(false);
    }
  };

  return (
    <Layout>
      <div className="verify-page">
        <h1 className="verify-page__title">Подтверждение Email</h1>
        <p className="verify-page__description">
          Мы отправили код подтверждения на {email}
        </p>
        
        <CodeInput
          length={CODE_LENGTH}
          onChange={setCode}
          onComplete={handleVerify}
          error={!!error}
          disabled={isLoading}
        />
        
        {error && (
          <div className="verify-page__error">
            {error}
          </div>
        )}
        
        <div className="verify-page__resend">
          {resendTimer > 0 ? (
            <span className="verify-page__timer">
              Отправить повторно через {resendTimer}с
            </span>
          ) : (
            <button
              className="verify-page__resend-btn"
              onClick={handleResend}
              disabled={isResending}
            >
              {isResending ? 'Отправка...' : 'Отправить код повторно'}
            </button>
          )}
        </div>
        
        {isLoading && <LoadingOverlay message="Проверка кода..." />}
      </div>
    </Layout>
  );
};