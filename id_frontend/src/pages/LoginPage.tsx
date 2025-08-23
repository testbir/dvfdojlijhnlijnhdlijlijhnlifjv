// ============= src/pages/LoginPage.tsx =============

import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { LoginForm } from '../components/AuthForm/LoginForm';
import { useAuth } from '../hooks/useAuth';
import { ROUTES } from '../utils/constants';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();
  
  const redirectUrl = searchParams.get('redirect_uri') || ROUTES.PROFILE;

  useEffect(() => {
    if (isAuthenticated) {
      navigate(redirectUrl);
    }
  }, [isAuthenticated, navigate, redirectUrl]);

  const handleSuccess = () => {
    navigate(redirectUrl);
  };

  return (
    <Layout>
      <LoginForm onSuccess={handleSuccess} redirectUrl={redirectUrl} />
    </Layout>
  );
};