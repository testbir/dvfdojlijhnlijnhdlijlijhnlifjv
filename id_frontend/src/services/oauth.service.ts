// src/services/oauth.service.ts

import { api, apiClient } from '../api/client';
import {
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
  generatePKCE(): { verifier: string; challenge: string } {
    const verifier = this.generateRandomString(128);
    const challenge = this.base64URLEncode(this.sha256(verifier));
    return { verifier, challenge };
  }

  private generateRandomString(length: number): string {
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
    let text = '';
    for (let i = 0; i < length; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }

  private sha256(plain: string): ArrayBuffer {
    const encoder = new TextEncoder();
    const data = encoder.encode(plain);
    return crypto.subtle.digest('SHA-256', data);
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

    return `/oauth/authorize?${searchParams.toString()}`;
  }

  /**
   * Обмен authorization code на токены
   */
  async exchangeCodeForTokens(params: TokenRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/oauth/token', params);
    const tokens = response.data;
    apiClient.saveTokens(tokens);
    return tokens;
  }

  /**
   * Обновление токенов через refresh token
   */
  async refreshTokens(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/oauth/token', {
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: process.env.REACT_APP_CLIENT_ID || 'id_frontend',
    });
    const tokens = response.data;
    apiClient.saveTokens(tokens);
    return tokens;
  }

  /**
   * Получение информации о пользователе
   */
  async getUserInfo(): Promise<UserInfo> {
    const response = await api.get<UserInfo>('/oauth/userinfo');
    return response.data;
  }

  /**
   * Получение информации о клиенте
   */
  async getClientInfo(clientId: string): Promise<OAuthClient> {
    const response = await api.get<OAuthClient>(`/api/clients/${clientId}`);
    return response.data;
  }

  /**
   * Отзыв токена
   */
  async revokeToken(token: string, tokenType: 'access_token' | 'refresh_token' = 'access_token'): Promise<void> {
    await api.post('/oauth/revoke', {
      token,
      token_type_hint: tokenType,
    });
  }

  /**
   * Авторизация с согласием пользователя
   */
  async authorizeWithConsent(
    authRequest: AuthorizationRequest,
    consent: boolean
  ): Promise<{ redirect_url: string }> {
    const response = await api.post<{ redirect_url: string }>('/oauth/authorize/consent', {
      ...authRequest,
      consent,
    });
    return response.data;
  }
}

export const oauthService = new OAuthService();