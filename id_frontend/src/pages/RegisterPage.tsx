// ============= src/pages/RegisterPage.tsx =============

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { RegisterForm } from '../components/AuthForm/RegisterForm';
import { useAuth } from '../hooks/useAuth';
import { ROUTES } from '../utils/constants';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      navigate(ROUTES.PROFILE);
    }
  }, [isAuthenticated, navigate]);

  const handleSuccess = (userId: string, email: string) => {
    navigate(`${ROUTES.VERIFY_EMAIL}?user_id=${userId}&email=${encodeURIComponent(email)}`);
  };

  return (
    <Layout>
      <RegisterForm onSuccess={handleSuccess} />
    </Layout>
  );
};