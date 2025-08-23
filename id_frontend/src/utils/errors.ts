// ============= src/utils/errors.ts =============

import { AxiosError } from 'axios';
import type { ApiError } from '../types/auth.types';
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

export const handleApiError = (error: unknown): string => {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as ApiError;
    
    if (apiError?.message) {
      return apiError.message;
    }
    
    if (apiError?.error) {
      return apiError.error;
    }
    
    switch (error.response?.status) {
      case 400:
        return ERROR_MESSAGES.VALIDATION_ERROR;
      case 401:
        return ERROR_MESSAGES.UNAUTHORIZED;
      case 403:
        return ERROR_MESSAGES.FORBIDDEN;
      case 404:
        return ERROR_MESSAGES.NOT_FOUND;
      case 500:
      case 502:
      case 503:
        return ERROR_MESSAGES.SERVER_ERROR;
      default:
        if (!error.response) {
          return ERROR_MESSAGES.NETWORK_ERROR;
        }
        return ERROR_MESSAGES.UNKNOWN_ERROR;
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
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