// ============= src/services/auth.service.ts =============

import { api } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
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
import { apiClient } from '../api/client';

class AuthService {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, data);
    if (response.data.access_token) {
      apiClient.saveTokens(response.data);
    }
    return response.data;
  }

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await api.post<RegisterResponse>(API_ENDPOINTS.AUTH.REGISTER, data);
    return response.data;
  }

  async verifyEmail(data: VerifyEmailRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(API_ENDPOINTS.AUTH.VERIFY_EMAIL, data);
    if (response.data.access_token) {
      apiClient.saveTokens(response.data);
    }
    return response.data;
  }

  async resendVerificationCode(userId: string): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH.RESEND_CODE, { user_id: userId });
  }

  async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, data);
  }

  async resetPassword(data: ResetPasswordRequest): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, data);
  }

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>(API_ENDPOINTS.AUTH.ME);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await api.post(API_ENDPOINTS.SESSION.LOGOUT);
    } finally {
      apiClient.logout();
    }
  }

  async checkSession(): Promise<boolean> {
    try {
      const response = await api.get(API_ENDPOINTS.SESSION.STATUS);
      return response.data.active;
    } catch {
      return false;
    }
  }
}

export const authService = new AuthService();