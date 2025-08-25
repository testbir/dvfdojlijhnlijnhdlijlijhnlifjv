// ============= src/pages/AuthorizePage.tsx =============

import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { LoadingOverlay } from '../components/LoadingOverlay/LoadingOverlay';
import { useAuth } from '../hooks/useAuth';
import { useOAuth } from '../hooks/useOAuth';
import { oauthService } from '../services/oauth.service';
import { ROUTES } from '../utils/constants';

export const AuthorizePage: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { initializeAuthorization, authorizeWithConsent, isProcessing, error } = useOAuth();
  
  const [authRequest, setAuthRequest] = useState<any>(null);
  const [clientInfo, setClientInfo] = useState<any>(null);
  const [isLoadingClient, setIsLoadingClient] = useState(true);

  useEffect(() => {
    const init = async () => {
      const request = await initializeAuthorization();
      if (request) {
        setAuthRequest(request);
        
        // Загружаем информацию о клиенте
        try {
          const client = await oauthService.getClientInfo(request.client_id);
          setClientInfo(client);
        } catch (err) {
          console.error('Failed to load client info:', err);
        }
      }
      setIsLoadingClient(false);
    };
    
    init();
  }, [initializeAuthorization]);

  if (authLoading || isLoadingClient) {
    return <LoadingOverlay message="Загрузка..." />;
  }

  if (!isAuthenticated) {
    const currentUrl = window.location.href;
    return <Navigate to={`${ROUTES.LOGIN}?redirect_uri=${encodeURIComponent(currentUrl)}`} />;
  }

  if (error || !authRequest) {
    return (
      <Layout>
        <div className="authorize-page">
          <div className="authorize-page__error">
            <h2>Ошибка авторизации</h2>
            <p>{error || 'Неверные параметры запроса'}</p>
          </div>
        </div>
      </Layout>
    );
  }

  const handleApprove = () => {
    authorizeWithConsent(authRequest, true);
  };

  const handleDeny = () => {
    authorizeWithConsent(authRequest, false);
  };

  return (
    <Layout>
      <div className="authorize-page">
        <div className="authorize-page__card">
          {clientInfo?.logo_uri && (
            <img 
              src={clientInfo.logo_uri} 
              alt={clientInfo.client_name}
              className="authorize-page__logo"
            />
          )}
          
          <h2 className="authorize-page__title">
            {clientInfo?.client_name || authRequest.client_id} запрашивает доступ
          </h2>
          
          <div className="authorize-page__scopes">
            <p>Приложение запрашивает следующие разрешения:</p>
            <ul>
              {authRequest.scope.split(' ').map((scope: string) => (
                <li key={scope}>{getScopeDescription(scope)}</li>
              ))}
            </ul>
          </div>
          
          <div className="authorize-page__actions">
            <button
              className="authorize-page__deny"
              onClick={handleDeny}
              disabled={isProcessing}
            >
              Отклонить
            </button>
            <button
              className="authorize-page__approve"
              onClick={handleApprove}
              disabled={isProcessing}
            >
              Разрешить
            </button>
          </div>
        </div>
        
        {isProcessing && <LoadingOverlay message="Обработка..." />}
      </div>
    </Layout>
  );
};

function getScopeDescription(scope: string): string {
  const descriptions: Record<string, string> = {
    openid: 'Базовая информация профиля',
    profile: 'Имя и фото профиля',
    email: 'Адрес электронной почты',
    offline_access: 'Доступ к данным в автономном режиме',
  };
  return descriptions[scope] || scope;
}
