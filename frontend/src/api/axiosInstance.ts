// frontend/src/api/axiosInstance.ts

import axios from "axios";
import type { AxiosInstance, AxiosError } from "axios";

interface AuthTokens {
  access: string;
  refresh: string;
}

/**
 * Создаёт axios-инстанс с поддержкой refresh токенов для микросервисов
 */
export const createApi = (baseURL: string): AxiosInstance => {
  const instance = axios.create({
    baseURL,
    withCredentials: true,
    timeout: 30000,
  });

  // Добавление access токена в заголовки
  instance.interceptors.request.use(config => {
    const raw = localStorage.getItem("auth_tokens");
    const tokens: AuthTokens | null = raw ? JSON.parse(raw) : null;

    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }

    return config;
  });

  // Обработка ответов и refresh токенов
  instance.interceptors.response.use(
    response => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as any;

      // Если 401 и еще не пробовали обновить токен
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const raw = localStorage.getItem("auth_tokens");
          const tokens: AuthTokens | null = raw ? JSON.parse(raw) : null;

          if (tokens?.refresh) {
            // Обновляем токен
            const response = await axios.post("/auth-api/api/token/refresh/", {
              refresh: tokens.refresh
            });

            const newTokens: AuthTokens = {
              access: response.data.access,
              refresh: response.data.refresh || tokens.refresh
            };

            localStorage.setItem("auth_tokens", JSON.stringify(newTokens));

            // Повторяем оригинальный запрос с новым токеном
            originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
            return instance(originalRequest);
          }
        } catch (refreshError) {
          // Refresh не удался - перенаправляем на логин
          localStorage.removeItem("auth_tokens");
          window.location.href = "/login";
          return Promise.reject(refreshError);
        }
      }

      // Для других ошибок или если refresh не помог
      if (error.response?.status === 401) {
        localStorage.removeItem("auth_tokens");
        window.location.href = "/login";
      }

      return Promise.reject(error);
    }
  );

  return instance;
};