// ============= src/types/auth.types.ts =============

export interface User {
  id: string;
  username: string;
  email: string;
  email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest { email: string; password: string; }
export interface RegisterRequest { username: string; email: string; password: string; password_confirm: string; }
export interface VerifyEmailRequest { user_id: string; code: string; }
export interface ForgotPasswordRequest { email: string; }
export interface ResetPasswordRequest {
  user_id: string;
  code: string;
  new_password: string;
  new_password_confirm: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  message: string;
  requires_verification: boolean;
}

export interface ApiError {
  error: string;
  message?: string;
  details?: Record<string, any>;
}
