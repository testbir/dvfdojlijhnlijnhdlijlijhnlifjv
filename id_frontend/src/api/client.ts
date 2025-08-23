// ============= src/api/client.ts =============

import axios, { type AxiosInstance, AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { type TokenResponse } from '../types/oauth.types'
import {
  TOKEN_STORAGE_KEY,
  REFRESH_TOKEN_STORAGE_KEY,
  ID_TOKEN_STORAGE_KEY,
} from '../utils/constants'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

class ApiClient {
  private client: AxiosInstance
  private refreshPromise: Promise<TokenResponse> | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,          // '' в dev, '/idp' в prod
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true,
    })
    this.setupInterceptors()
  }

  private setupInterceptors() {
    this.client.interceptors.request.use((config) => {
      const token = this.getAccessToken()
      if (token) {
        config.headers = { ...config.headers, Authorization: `Bearer ${token}` }
      }
      return config
    })

    this.client.interceptors.response.use(
      (r) => r,
      async (error: AxiosError) => {
        const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined
        const status = error.response?.status
        const url = original?.url || ''
        // не рефрешим сам /oauth/token и избегаем циклов
        if (
          status === 401 &&
          original &&
          !original._retry &&
          !url.startsWith('/oauth/token') &&
          this.getRefreshToken()
        ) {
          original._retry = true
          try {
            await this.refreshToken()
            const token = this.getAccessToken()
            if (token && original.headers) original.headers.Authorization = `Bearer ${token}`
            return this.client(original)
          } catch (e) {
            this.clearTokens()
            window.location.href = '/login'
            throw e
          }
        }
        throw error
      }
    )
  }

  private getAccessToken() { return localStorage.getItem(TOKEN_STORAGE_KEY) }
  private getRefreshToken() { return localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY) }

  private setTokens(tokens: TokenResponse) {
    localStorage.setItem(TOKEN_STORAGE_KEY, tokens.access_token)
    if (tokens.refresh_token) localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, tokens.refresh_token)
    if (tokens.id_token) localStorage.setItem(ID_TOKEN_STORAGE_KEY, tokens.id_token)
  }

  private clearTokens() {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
    localStorage.removeItem(ID_TOKEN_STORAGE_KEY)
  }

private async refreshToken(): Promise<TokenResponse> {
  if (this.refreshPromise) return this.refreshPromise
  const refreshToken = this.getRefreshToken()
  if (!refreshToken) throw new Error('No refresh token')

  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: refreshToken,
    client_id: import.meta.env.VITE_CLIENT_ID || 'id_frontend',
  })

  this.refreshPromise = this.client
    .post<TokenResponse>('/oauth/token', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    .then(({ data }) => { this.setTokens(data); this.refreshPromise = null; return data })
    .catch((e) => { this.refreshPromise = null; throw e })

  return this.refreshPromise
}

  getClient() { return this.client }
  saveTokens(tokens: TokenResponse) { this.setTokens(tokens) }
  logout() { this.clearTokens() }
}

export const apiClient = new ApiClient()
export const api = apiClient.getClient()
