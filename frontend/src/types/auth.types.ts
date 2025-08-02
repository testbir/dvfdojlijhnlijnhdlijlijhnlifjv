// src/types/auth.types.ts

export interface User {
  id: number;
  email: string;
  username: string;
  is_email_confirmed: boolean;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password1: string;
  password2: string;
}

export interface VerifyCodeData {
  user_id: number;
  code: string;
}

export interface RequestResetData {
  email: string;
}

export interface VerifyResetCodeData {
  email: string;
  code: string;
}

export interface SetNewPasswordData {
  user_id: number;
  password1: string;
  password2: string;
}