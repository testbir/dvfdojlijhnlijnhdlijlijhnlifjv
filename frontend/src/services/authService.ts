// arc/services/authService.tsx


import authApi from "../api/authApi";
import type {
  AuthTokens,
  LoginData,
  RegisterData,
  VerifyCodeData,
  RequestResetData,
  VerifyResetCodeData,
  SetNewPasswordData,
} from "../types/auth.types";

const TOKEN_KEY = "auth_tokens";

class AuthService {
  // Сохранение токенов
  setTokens(tokens: AuthTokens) {
    localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
  }

  // Получение токенов
  getTokens(): AuthTokens | null {
    const tokens = localStorage.getItem(TOKEN_KEY);
    return tokens ? JSON.parse(tokens) : null;
  }

  // Удаление токенов
  removeTokens() {
    localStorage.removeItem(TOKEN_KEY);
  }

  // Вход
  async login(data: LoginData): Promise<AuthTokens> {
    const response = await authApi.post("/api/token/", data);
    const tokens = response.data;
    this.setTokens(tokens);
    return tokens;
  }

  // Регистрация
  async register(data: RegisterData) {
    const response = await authApi.post("/api/register/", data);
    return response.data;
  }

  // Подтверждение email
  async verifyCode(data: VerifyCodeData) {
    const response = await authApi.post("/api/verify-code/", data);
    return response.data;
  }

  // Запрос на сброс пароля
  async requestPasswordReset(data: RequestResetData) {
    const response = await authApi.post("/api/request-reset/", data);
    return response.data;
  }

  // Проверка кода сброса
  async verifyResetCode(data: VerifyResetCodeData) {
    const response = await authApi.post("/api/verify-reset-code/", data);
    return response.data;
  }

  // Установка нового пароля
  async setNewPassword(data: SetNewPasswordData) {
    const response = await authApi.post("/api/set-new-password/", data);
    return response.data;
  }

  // Выход
  async logout() {
    const tokens = this.getTokens();
    if (tokens?.refresh) {
      try {
        await authApi.post("/api/logout/", { refresh: tokens.refresh });
      } catch (error) {
        console.error("Ошибка при выходе:", error);
      }
    }
    this.removeTokens();
  }

  // Обновление access токена
  async refreshToken(): Promise<string | null> {
    const tokens = this.getTokens();
    if (!tokens?.refresh) return null;

    try {
      const response = await authApi.post("/api/token/refresh/", {
        refresh: tokens.refresh,
      });
      const newAccess = response.data.access;
      this.setTokens({ ...tokens, access: newAccess });
      return newAccess;
    } catch (error) {
      this.removeTokens();
      return null;
    }
  }
}

export default new AuthService();