// ============= src/services/oauth.service.ts =============

import { api, apiClient } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import type {
  AuthorizationRequest,
  TokenRequest,
  TokenResponse,
  UserInfo,
  OAuthClient,
} from '../types/oauth.types';

class OAuthService {
  /**
   * Генерация PKCE verifier и challenge
   */
  async generatePKCE(): Promise<{ verifier: string; challenge: string }> {
    const verifier = this.generateRandomString(128);
    const encoder = new TextEncoder();
    const data = encoder.encode(verifier);
    const digest = await crypto.subtle.digest('SHA-256', data);
    const challenge = this.base64URLEncode(digest);
    return { verifier, challenge };
  }

  private generateRandomString(length: number): string {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'
    const bytes = new Uint8Array(length)
    crypto.getRandomValues(bytes)
    return Array.from(bytes, b => charset[b % charset.length]).join('')
  }


  private base64URLEncode(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let str = '';
    for (const byte of bytes) {
      str += String.fromCharCode(byte);
    }
    return btoa(str)
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  }

  /**
   * Построение URL для авторизации
   */
  buildAuthorizationUrl(params: AuthorizationRequest): string {
    const searchParams = new URLSearchParams({
      client_id: params.client_id,
      redirect_uri: params.redirect_uri,
      response_type: params.response_type,
      scope: params.scope,
    });

    if (params.state) searchParams.append('state', params.state);
    if (params.code_challenge) searchParams.append('code_challenge', params.code_challenge);
    if (params.code_challenge_method) searchParams.append('code_challenge_method', params.code_challenge_method);
    if (params.nonce) searchParams.append('nonce', params.nonce);
    if (params.prompt) searchParams.append('prompt', params.prompt);
    if (params.max_age) searchParams.append('max_age', params.max_age.toString());

    const base = import.meta.env.VITE_API_BASE || '';
    return `${base}${API_ENDPOINTS.OAUTH.AUTHORIZE}?${searchParams.toString()}`;
  }

  /**
   * Обмен authorization code на токены
   */
async exchangeCodeForTokens(params: TokenRequest): Promise<TokenResponse> {
  const body = new URLSearchParams({
    grant_type: params.grant_type,
    code: params.code ?? '',
    redirect_uri: params.redirect_uri ?? '',
    code_verifier: params.code_verifier ?? '',
    client_id: params.client_id,
  })
  const { data } = await api.post<TokenResponse>(API_ENDPOINTS.OAUTH.TOKEN, body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  apiClient.saveTokens(data)
  return data
}

async refreshTokens(refreshToken: string): Promise<TokenResponse> {
  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: refreshToken,
    client_id: import.meta.env.VITE_CLIENT_ID || 'id_frontend',
  })
  const { data } = await api.post<TokenResponse>(API_ENDPOINTS.OAUTH.TOKEN, body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  apiClient.saveTokens(data)
  return data
}

  /**
   * Получение информации о пользователе
   */
  async getUserInfo(): Promise<UserInfo> {
    const response = await api.get<UserInfo>(API_ENDPOINTS.OAUTH.USERINFO);
    return response.data;
  }

  /**
   * Получение информации о клиенте
   */
  async getClientInfo(clientId: string): Promise<OAuthClient> {
    const response = await api.get<OAuthClient>(API_ENDPOINTS.CLIENTS.GET(clientId));
    return response.data;
  }

  /**
   * Отзыв токена
   */
  async revokeToken(
    token: string,
    tokenType: 'access_token' | 'refresh_token' = 'access_token'
  ): Promise<void> {
    const body = new URLSearchParams({ token, token_type_hint: tokenType });
    await api.post(API_ENDPOINTS.OAUTH.REVOKE, body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  }

  /**
   * Авторизация с согласием пользователя
   */
  async authorizeWithConsent(
    authRequest: AuthorizationRequest,
    consent: boolean
  ): Promise<{ redirect_url: string }> {
    const response = await api.post<{ redirect_url: string }>(API_ENDPOINTS.OAUTH.CONSENT, {
      ...authRequest,
      consent,
    });
    return response.data;
  }
}

export const oauthService = new OAuthService();