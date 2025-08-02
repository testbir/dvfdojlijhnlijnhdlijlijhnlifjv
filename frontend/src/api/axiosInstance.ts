// 📦 src/api/axiosInstance.ts

import axios from "axios";
import type { AxiosInstance } from "axios";

/**
 * Создаёт axios-инстанс с базовыми настройками для конкретного микросервиса.
 * @param baseURL Базовый URL (например, /auth-api, /catalog-api)
 */
export const createApi = (baseURL: string): AxiosInstance => {
  const instance = axios.create({
    baseURL,
    withCredentials: true,
    timeout: 10000,
  });

  // 🔐 1. Добавление токена
  instance.interceptors.request.use(config => {
    const raw = localStorage.getItem("auth_tokens");
    const tokens = raw ? JSON.parse(raw) : null;

    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }

    return config;
  });

  // 🚨 2. Обработка 401
  instance.interceptors.response.use(
    response => response,
    error => {
      if (error.response?.status === 401) {
        console.warn("⚠️ Неавторизован. Возможен редирект на /login.");
        // window.location.href = "/login"; // Включить по желанию
      }
      return Promise.reject(error);
    }
  );

  return instance;
};
