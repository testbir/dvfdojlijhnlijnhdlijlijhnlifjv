// ============= src/utils/errors.ts =============

import { AxiosError } from 'axios';
import { ERROR_MESSAGES } from './constants';

export class AppError extends Error {
  public code?: string;
  public details?: any;

  constructor(message: string, code?: string, details?: any) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.details = details;
  }
}

// replace handleApiError with:
export const handleApiError = (error: unknown): string => {
  if (error instanceof AxiosError) {
    const data = error.response?.data as any;

    const flatten = (v: any): string => {
      if (!v) return '';
      if (typeof v === 'string') return v;
      if (Array.isArray(v)) return v.map(flatten).filter(Boolean).join('\n');
      if (typeof v === 'object') return Object.values(v).map(flatten).filter(Boolean).join('\n') || JSON.stringify(v);
      return String(v);
    };

    const msg =
      flatten(data?.message) ||
      flatten(data?.error) ||
      flatten(data?.details);

    if (msg) return msg;

    switch (error.response?.status) {
      case 400: return ERROR_MESSAGES.VALIDATION_ERROR;
      case 401: return ERROR_MESSAGES.UNAUTHORIZED;
      case 403: return ERROR_MESSAGES.FORBIDDEN;
      case 404: return ERROR_MESSAGES.NOT_FOUND;
      case 500:
      case 502:
      case 503: return ERROR_MESSAGES.SERVER_ERROR;
      default:
        return error.response ? ERROR_MESSAGES.UNKNOWN_ERROR : ERROR_MESSAGES.NETWORK_ERROR;
    }
  }
  if (error instanceof Error) return error.message;
  return ERROR_MESSAGES.UNKNOWN_ERROR;
};


export const isNetworkError = (error: unknown): boolean => {
  if (error instanceof AxiosError) {
    return !error.response && error.code === 'ERR_NETWORK';
  }
  return false;
};

export const isUnauthorizedError = (error: unknown): boolean => {
  if (error instanceof AxiosError) {
    return error.response?.status === 401;
  }
  return false;
};