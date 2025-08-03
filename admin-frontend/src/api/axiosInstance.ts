// src/api/axiosInstance.ts


import axios from 'axios';

const api = axios.create({
  baseURL: 'http://adminservice:8002', 
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');

  if (token && config && config.headers && !config.url?.includes('/auth/login')) {
    // Убедимся, что headers имеет правильный тип
    (config.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
