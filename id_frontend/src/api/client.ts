// ============= src/api/client.ts =============
import axios, {
  type AxiosInstance,
  type AxiosError,
  type InternalAxiosRequestConfig,
  AxiosHeaders,
} from 'axios'
import { type TokenResponse } from '../types/oauth.types'
import {
  TOKEN_STORAGE_KEY,
  REFRESH_TOKEN_STORAGE_KEY,
  ID_TOKEN_STORAGE_KEY,
} from '../utils/constants'

const API_BASE = import.meta.env.VITE_API_BASE ?? '' // '' в dev, '/idp' в prod

class ApiClient {
  private client: AxiosInstance
  private refreshPromise: Promise<TokenResponse> | null = null
  private csrfToken: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true,
    })
    this.setupInterceptors()
  }

  // ---------- Interceptors ----------
  private setupInterceptors() {
    this.client.interceptors.request.use(async (config) => {
      const headers = (config.headers ??= new AxiosHeaders(config.headers))
      const token = this.getAccessToken()
      if (token) headers.set('Authorization', `Bearer ${token}`)

      if (this.needsCsrf(config)) {
        // лениво получаем CSRF из ответа или cookie
        if (!this.csrfToken && !this.getCookie('csrf_token')) {
          await this.fetchCsrf()
        }
        const csrf = this.csrfToken || this.getCookie('csrf_token')
        if (csrf) headers.set('X-CSRF-Token', csrf)

      }
      return config
    })

    

    this.client.interceptors.response.use(
      (r) => r,
      async (error: AxiosError) => {
        const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined
        const status = error.response?.status
        const url = original?.url || ''

        // Не пытаемся рефрешить /oauth/token|/oauth/revoke и избегаем циклов
        const isTokenEndpoint = url.startsWith('/token') || url.startsWith('/revoke')
        if (status === 401 && original && !original._retry && !isTokenEndpoint && this.getRefreshToken()) {

          original._retry = true
          try {
            await this.refreshToken()
            const token = this.getAccessToken()
            if (token && original.headers) (original.headers as AxiosHeaders).set('Authorization', `Bearer ${token}`)
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

  private async fetchCsrf(): Promise<string | null> {
    try {
      const resp = await this.client.get('/api/auth/csrf', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      })
      const headers = resp.headers as any
      const fromHeader = headers['x-csrf-token'] || headers['x-csrf']
      const body: any = resp.data
      const fromBody = body?.csrf || body?.csrf_token || body?.token
      const fromCookie = this.getCookie('csrf_token')
      const token = fromHeader || fromBody || fromCookie || null
      this.csrfToken = token
      return token
    } catch {
      return null
    }
  }


  // ---------- Helpers ----------
  private getAccessToken() {
    return localStorage.getItem(TOKEN_STORAGE_KEY)
  }
  private getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)
  }
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

  private getCookie(name: string): string | null {
    const m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)'))
    return m ? decodeURIComponent(m[1]) : null
  }

private needsCsrf(config: InternalAxiosRequestConfig): boolean {
  const method = (config.method ?? 'get').toUpperCase()
  if (method === 'GET' || method === 'HEAD' || method === 'OPTIONS') return false
  const url = config.url ?? ''

  // исключения
  if (
    url.startsWith('/token') ||            url.startsWith('/revoke') ||       
    url.startsWith('/api/auth/csrf') ||
    url.startsWith('/.well-known') ||
    url.startsWith('/health')
  ) { return false }

  // вот здесь добавляем oauth/authorize (закроет POST /oauth/authorize/consent)
  return (
    url.startsWith('/api/auth/') ||
    url.startsWith('/api/account/') ||
    url.startsWith('/authorize')
    // при необходимости — если logout у вас под CSRF:
    // || url.startsWith('/api/session/')
  )
}

  // ---------- Refresh ----------
  private async refreshToken(): Promise<TokenResponse> {
    if (this.refreshPromise) return this.refreshPromise

    const refreshToken = this.getRefreshToken()
    if (!refreshToken) throw new Error('No refresh token')

    const body = new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      // Для public-клиента client_id обязателен
      client_id: import.meta.env.VITE_CLIENT_ID || 'id_frontend',
    })

      this.refreshPromise = this.client
        .post<TokenResponse>('/token', body, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
      .then(({ data }) => {
        this.setTokens(data)
        this.refreshPromise = null
        return data
      })
      .catch((e) => {
        this.refreshPromise = null
        throw e
      })

    return this.refreshPromise
  }

  // ---------- Public API ----------
  getClient() {
    return this.client
  }
  saveTokens(tokens: TokenResponse) {
    this.setTokens(tokens)
  }
  logout() {
    this.clearTokens()
  }
}

export const apiClient = new ApiClient()
export const api = apiClient.getClient()
