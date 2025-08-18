// frontend/src/services/authService.ts

import { authApi } from "../api/authApi";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
}

class AuthService {
  // Вход с новым форматом токенов
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    try {
      const response = await authApi.post("/api/token/", credentials);
      const tokens: AuthTokens = {
        access: response.data.access,
        refresh: response.data.refresh
      };
      
      localStorage.setItem("auth_tokens", JSON.stringify(tokens));
      return tokens;
    } catch (error: any) {
      // Обработка специфичных ошибок
      if (error.response?.data?.error === 'account_not_activated') {
        throw {
          type: 'NOT_ACTIVATED',
          message: error.response.data.message,
          userId: error.response.data.user_id,
          email: error.response.data.email
        };
      }
      throw error;
    }
  }

  // Регистрация
  async register(data: RegisterData): Promise<{ user_id: number; message: string }> {
    const response = await authApi.post("/api/register/", data);
    return response.data;
  }

  // Подтверждение email
  async verifyCode(userId: number, code: string): Promise<AuthTokens> {
    const response = await authApi.post("/api/verify-code/", {
      user_id: userId,
      code: code
    });
    
    const tokens: AuthTokens = {
      access: response.data.access,
      refresh: response.data.refresh
    };
    
    localStorage.setItem("auth_tokens", JSON.stringify(tokens));
    return tokens;
  }

  // Повторная отправка кода
  async resendCode(userId: number, purpose: string = 'register'): Promise<void> {
    await authApi.post("/api/resend-code/", {
      user_id: userId,
      purpose: purpose
    });
  }

  // Запрос сброса пароля
  async requestPasswordReset(email: string): Promise<void> {
    await authApi.post("/api/request-reset/", { email });
  }

  // Подтверждение кода сброса
  async verifyResetCode(email: string, code: string): Promise<{ user_id: number }> {
    const response = await authApi.post("/api/verify-reset-code/", {
      email,
      code
    });
    return response.data;
  }

  // Установка нового пароля
  async setNewPassword(userId: number, password: string): Promise<void> {
    await authApi.post("/api/set-new-password/", {
      user_id: userId,
      password: password
    });
  }

  // Выход
  async logout(): Promise<void> {
    try {
      const raw = localStorage.getItem("auth_tokens");
      const tokens: AuthTokens | null = raw ? JSON.parse(raw) : null;
      
      if (tokens?.refresh) {
        await authApi.post("/api/logout/", {
          refresh: tokens.refresh
        });
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem("auth_tokens");
      window.location.href = "/login";
    }
  }

  // Получение данных пользователя
  async getCurrentUser(): Promise<User> {
    const response = await authApi.get("/api/user/");
    return response.data;
  }

  // Проверка авторизации
  isAuthenticated(): boolean {
    const raw = localStorage.getItem("auth_tokens");
    const tokens: AuthTokens | null = raw ? JSON.parse(raw) : null;
    return !!tokens?.access;
  }

  // Получение токенов
  getTokens(): AuthTokens | null {
    const raw = localStorage.getItem("auth_tokens");
    return raw ? JSON.parse(raw) : null;
  }
}

export default new AuthService();