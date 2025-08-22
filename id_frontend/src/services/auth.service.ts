// src/services/auth.service.ts

import { api } from '../api/client';
import {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  VerifyEmailRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  User,
} from '../types/auth.types';

class AuthService {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/login', data);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await api.post<RegisterResponse>('/api/auth/register', data);
    return response.data;
  }

  async verifyEmail(data: VerifyEmailRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/verify-email', data);
    return response.data;
  }

  async resendVerificationCode(userId: string): Promise<void> {
    await api.post('/api/auth/resend-code', { user_id: userId });
  }

  async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    await api.post('/api/auth/forgot-password', data);
  }

  async resetPassword(data: ResetPasswordRequest): Promise<void> {
    await api.post('/api/auth/reset-password', data);
  }

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  }

  async logout(): Promise<void> {
    await api.post('/api/session/logout');
    apiClient.logout();
  }

  async checkSession(): Promise<boolean> {
    try {
      const response = await api.get('/api/session/status');
      return response.data.active;
    } catch {
      return false;
    }
  }
}

export const authService = new AuthService();