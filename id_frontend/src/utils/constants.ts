// ============= src/utils/constants.ts =============

export const APP_NAME = 'ID Service';
export const APP_VERSION = '1.0.0';

export const PASSWORD_MIN_LENGTH = 8;
export const USERNAME_MIN_LENGTH = 3;
export const USERNAME_MAX_LENGTH = 20;

export const CODE_LENGTH = 6;
export const CODE_RESEND_TIMEOUT = 60; // seconds

export const TOKEN_STORAGE_KEY = 'access_token';
export const REFRESH_TOKEN_STORAGE_KEY = 'refresh_token';
export const ID_TOKEN_STORAGE_KEY = 'id_token';

export const OAUTH_SCOPES = {
  OPENID: 'openid',
  PROFILE: 'profile',
  EMAIL: 'email',
  OFFLINE_ACCESS: 'offline_access',
};

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Ошибка сети. Проверьте подключение к интернету.',
  UNAUTHORIZED: 'Необходима авторизация.',
  FORBIDDEN: 'Доступ запрещен.',
  NOT_FOUND: 'Ресурс не найден.',
  VALIDATION_ERROR: 'Проверьте правильность введенных данных.',
  SERVER_ERROR: 'Ошибка сервера. Попробуйте позже.',
  UNKNOWN_ERROR: 'Произошла неизвестная ошибка.',
};

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  VERIFY_EMAIL: '/verify-email',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  PROFILE: '/profile',
  AUTHORIZE: '/oauth/authorize',
  ERROR: '/error',
};