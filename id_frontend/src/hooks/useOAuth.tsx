// ============= src/hooks/useOAuth.tsx =============

import { useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { oauthService } from '../services/oauth.service';
import { storageService } from '../services/storage.service';
import type { AuthorizationRequest } from '../types/oauth.types';
import { ROUTES } from '../utils/constants';

export const useOAuth = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initializeAuthorization = useCallback(async () => {
    // Получаем параметры из URL
    const clientId = searchParams.get('client_id');
    const redirectUri = searchParams.get('redirect_uri');
    const responseType = searchParams.get('response_type') || 'code';
    const scope = searchParams.get('scope') || 'openid profile email';
    const state = searchParams.get('state') || undefined;
    const nonce = searchParams.get('nonce') || undefined;
    const prompt = searchParams.get('prompt') as any || undefined;

    if (!clientId || !redirectUri) {
      setError('Отсутствуют обязательные параметры');
      return null;
    }

    // Генерируем PKCE
    const pkce = await oauthService.generatePKCE();
    
    // Сохраняем данные для последующего использования
    const authRequest: AuthorizationRequest = {
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: responseType as 'code' | 'token',
      scope,
      state,
      code_challenge: pkce.challenge,
      code_challenge_method: 'S256',
      nonce,
      prompt,
    };

    // Сохраняем в storage
    if (state) {
      storageService.saveOAuthState(state, authRequest);
      storageService.savePKCEVerifier(state, pkce.verifier);
    }

    return authRequest;
  }, [searchParams]);

  const authorizeWithConsent = useCallback(async (
    authRequest: AuthorizationRequest,
    consent: boolean
  ) => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await oauthService.authorizeWithConsent(authRequest, consent);
      
      if (response.redirect_url) {
        window.location.href = response.redirect_url;
      }
    } catch (err: any) {
      setError(err.message || 'Ошибка авторизации');
      setIsProcessing(false);
    }
  }, []);

  const handleCallback = useCallback(async () => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');

    if (error) {
      navigate(`${ROUTES.ERROR}?error=${error}&description=${searchParams.get('error_description')}`);
      return;
    }

    if (!code || !state) {
      navigate(`${ROUTES.ERROR}?error=invalid_request`);
      return;
    }

    setIsProcessing(true);

    try {
      // Получаем сохраненные данные
      const authRequest = storageService.getAndRemoveOAuthState(state);
      const verifier = storageService.getPKCEVerifier(state);

      if (!authRequest || !verifier) {
        throw new Error('Invalid state or expired session');
      }

      // Обмениваем код на токены
      await oauthService.exchangeCodeForTokens({
        grant_type: 'authorization_code',
        code,
        redirect_uri: authRequest.redirect_uri,
        code_verifier: verifier,
        client_id: authRequest.client_id,
      });

      // Перенаправляем на профиль или главную
      navigate(ROUTES.PROFILE);
    } catch (err: any) {
      navigate(`${ROUTES.ERROR}?error=exchange_failed`);
    } finally {
      setIsProcessing(false);
    }
  }, [navigate, searchParams]);

  return {
    initializeAuthorization,
    authorizeWithConsent,
    handleCallback,
    isProcessing,
    error,
  };
};