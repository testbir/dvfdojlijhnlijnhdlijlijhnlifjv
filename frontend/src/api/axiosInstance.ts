// frontend/src/api/axiosInstance.ts
import axios from "axios";
import type { AxiosInstance } from "axios";

// Создаем типизированную функцию для создания API клиентов
export const createApi = (baseURL: string): AxiosInstance => {
  const instance = axios.create({
    baseURL,
    timeout: 30000,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Request interceptor для добавления токена
  instance.interceptors.request.use(
    (config) => {
      const authData = localStorage.getItem("auth_tokens");
      if (authData) {
        try {
          const tokens = JSON.parse(authData);
          if (tokens.access) {
            config.headers.Authorization = `Bearer ${tokens.access}`;
          }
        } catch (error) {
          console.error("Error parsing auth tokens:", error);
        }
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor для обработки ошибок
  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // Обработка 401 ошибки (токен истек)
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const authData = localStorage.getItem("auth_tokens");
          if (authData) {
            const tokens = JSON.parse(authData);
            if (tokens.refresh) {
              // Пытаемся обновить токен
              const refreshResponse = await axios.post("/auth-api/api/token/refresh/", {
                refresh: tokens.refresh,
              });

              const newTokens = {
                access: refreshResponse.data.access,
                refresh: tokens.refresh, // Сохраняем старый refresh токен
              };

              localStorage.setItem("auth_tokens", JSON.stringify(newTokens));
              
              // Повторяем оригинальный запрос с новым токеном
              originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
              return instance(originalRequest);
            }
          }
        } catch (refreshError) {
          // Если обновление токена не удалось, перенаправляем на логин
          localStorage.removeItem("auth_tokens");
          window.location.href = "/login";
          return Promise.reject(refreshError);
        }
      }

      // Обработка других ошибок
      if (error.response?.status === 403) {
        console.error("Доступ запрещен:", error.response.data);
      }

      return Promise.reject(error);
    }
  );

  return instance;
};

// Экспорт конкретных API клиентов с новыми версионированными путями
export const authApi = createApi("/auth-api");
export const catalogApi = createApi("/catalog-api");
export const learningApi = createApi("/learning-api");
export const pointsApi = createApi("/points-api");