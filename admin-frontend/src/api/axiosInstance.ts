// src/api/axiosInstance.ts
import axios from 'axios';

const api = axios.create({
  baseURL: '/admin-api/', // ← завершающий слэш
  timeout: 100000,
});

// Нормализация URL
api.interceptors.request.use((config) => {
  if (config.url) {
    const [path, qs = ''] = config.url.split('?');
    const normalizedPath = path
      .replace(/^\/+/, '')
      .replace(/\/{2,}/g, '/');

    // ДОБАВЬ ЭТО:
    let p = normalizedPath;
    // срежем завершающий слэш после числового id: /xxx/123/ → /xxx/123
    p = p.replace(/\/(\d+)\/$/, '/$1');

    config.url = p + (qs ? '?' + qs : '');
  }
  return config;
}, Promise.reject);

// 401 хендлер как был…
api.interceptors.response.use(
  (r) => r,
  (e) => {
    if (e.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(e);
  }
);

export default api;
