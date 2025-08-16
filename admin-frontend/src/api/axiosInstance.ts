// src/api/axiosInstance.ts


import axios from 'axios';

const api = axios.create({
  baseURL: '/admin-api', // Через proxy
  timeout: 100000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    
    if (token && config.headers && !config.url?.includes('/auth/login')) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.request.use((config) => {
  const t = localStorage.getItem('token');
  if (t && config.headers && !config.url?.includes('/auth/login')) {
    config.headers.Authorization = `Bearer ${t}`;
  }
  console.log('[API]', config.method?.toUpperCase(), config.url); // ← кто зовёт /admin/courses
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;