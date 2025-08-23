// ============= src/pages/ProfilePage.tsx =============

import React from 'react';
import { Navigate } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { LoadingOverlay } from '../components/LoadingOverlay/LoadingOverlay';
import { useAuth } from '../hooks/useAuth';
import { ROUTES } from '../utils/constants';
import '../styles/pages.scss';

export const ProfilePage: React.FC = () => {
  const { user, isLoading, isAuthenticated, logout } = useAuth();

  if (isLoading) {
    return <LoadingOverlay message="Загрузка профиля..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} />;
  }

  const handleLogout = async () => {
    await logout();
  };

  return (
    <Layout>
      <div className="profile-page">
        <h1 className="profile-page__title">Профиль</h1>
        
        <div className="profile-page__card">
          <div className="profile-page__info">
            <div className="profile-page__field">
              <span className="profile-page__label">Имя пользователя:</span>
              <span className="profile-page__value">{user?.username}</span>
            </div>
            
            <div className="profile-page__field">
              <span className="profile-page__label">Email:</span>
              <span className="profile-page__value">
                {user?.email}
                {user?.email_verified && (
                  <span className="profile-page__verified">✓</span>
                )}
              </span>
            </div>
            
            <div className="profile-page__field">
              <span className="profile-page__label">ID:</span>
              <span className="profile-page__value">{user?.id}</span>
            </div>
          </div>
          
          <button
            className="profile-page__logout"
            onClick={handleLogout}
          >
            Выйти
          </button>
        </div>
      </div>
    </Layout>
  );
};