/* ============= src/services/auth.service.ts ============= */

import { api, apiClient } from '../api/client'
import { API_ENDPOINTS } from '../api/endpoints'
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  VerifyEmailRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  User,
} from '../types/auth.types'
import { AppError } from '../utils/errors'

type RegisterPayload = {
  user_id: string
  email: string
  requires_verification: boolean
  message?: string
}

function assertRegisterPayload(r: any): asserts r is RegisterPayload {
  const ok =
    r &&
    typeof r.user_id === 'string' &&
    typeof r.email === 'string' &&
    typeof r.requires_verification === 'boolean'
  if (!ok) throw new AppError('Некорректный ответ сервера регистрации')
}

class AuthService {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, data)
    if (response.data.access_token) {
      apiClient.saveTokens(response.data)
    }
    return response.data
  }

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const { data: raw } = await api.post<unknown>(API_ENDPOINTS.AUTH.REGISTER, data)
    assertRegisterPayload(raw)
    return {
      user_id: raw.user_id,
      email: raw.email,
      message: raw.message ?? '',
      requires_verification: raw.requires_verification,
    }
  }

  async verifyEmail(data: VerifyEmailRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(API_ENDPOINTS.AUTH.VERIFY_EMAIL, data)
    if (response.data.access_token) {
      apiClient.saveTokens(response.data)
    }
    return response.data
  }

  async resendVerificationCode(userId: string): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH.RESEND_CODE, { user_id: userId })
  }

  async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, data)
  }

  async resetPassword(data: ResetPasswordRequest): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, data)
  }

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>(API_ENDPOINTS.AUTH.ME)
    return response.data
  }

  async logout(): Promise<void> {
    try {
      await api.post(API_ENDPOINTS.SESSION.LOGOUT)
    } finally {
      apiClient.logout()
    }
  }

  async checkSession(): Promise<boolean> {
    try {
      const response = await api.get(API_ENDPOINTS.SESSION.STATUS)
      return response.data.active
    } catch {
      return false
    }
  }
}

export const authService = new AuthService()
