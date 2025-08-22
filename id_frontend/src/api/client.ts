// src/api/client.ts

import axios, { type AxiosInstance, AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { type TokenResponse } from '../types/oauth.types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private refreshPromise: Promise<TokenResponse> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // для cookies
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = this.getAccessToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: AxiosError) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            await this.refreshToken();
            const token = this.getAccessToken();
            if (token && originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return this.client(originalRequest);
          } catch (refreshError) {
            this.clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private setTokens(tokens: TokenResponse) {
    localStorage.setItem('access_token', tokens.access_token);
    if (tokens.refresh_token) {
      localStorage.setItem('refresh_token', tokens.refresh_token);
    }
    if (tokens.id_token) {
      localStorage.setItem('id_token', tokens.id_token);
    }
  }

  private clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('id_token');
  }

  private async refreshToken(): Promise<TokenResponse> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    this.refreshPromise = this.client
      .post<TokenResponse>('/oauth/token', {
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
        client_id: process.env.REACT_APP_CLIENT_ID || 'id_frontend',
      })
      .then((response) => {
        const tokens = response.data;
        this.setTokens(tokens);
        this.refreshPromise = null;
        return tokens;
      })
      .catch((error) => {
        this.refreshPromise = null;
        throw error;
      });

    return this.refreshPromise;
  }

  public getClient(): AxiosInstance {
    return this.client;
  }

  public saveTokens(tokens: TokenResponse) {
    this.setTokens(tokens);
  }

  public logout() {
    this.clearTokens();
  }
}

export const apiClient = new ApiClient();
export const api = apiClient.getClient();