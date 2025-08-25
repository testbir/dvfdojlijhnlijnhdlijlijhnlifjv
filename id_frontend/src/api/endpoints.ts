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
    ME: '/api/account/profile',
  },
  
  // OAuth endpoints
  OAUTH: {
    AUTHORIZE: '/authorize',
    TOKEN: '/token',
    USERINFO: '/userinfo',
    REVOKE: '/revoke',
    CONSENT: '/authorize/consent',
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