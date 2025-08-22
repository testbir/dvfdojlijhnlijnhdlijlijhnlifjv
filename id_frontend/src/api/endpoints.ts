// ============= src/api/endpoints.ts =============

export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    VERIFY_EMAIL: '/api/auth/verify-email',
    RESEND_CODE: '/api/auth/resend-code',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    RESET_PASSWORD: '/api/auth/reset-password',
    ME: '/api/auth/me',
  },
  
  // OAuth endpoints
  OAUTH: {
    AUTHORIZE: '/oauth/authorize',
    TOKEN: '/oauth/token',
    USERINFO: '/oauth/userinfo',
    REVOKE: '/oauth/revoke',
    JWKS: '/.well-known/jwks.json',
    DISCOVERY: '/.well-known/openid-configuration',
  },
  
  // Session endpoints
  SESSION: {
    LOGOUT: '/api/session/logout',
    STATUS: '/api/session/status',
  },
  
  // Client endpoints
  CLIENTS: {
    GET: (clientId: string) => `/api/clients/${clientId}`,
  },
};