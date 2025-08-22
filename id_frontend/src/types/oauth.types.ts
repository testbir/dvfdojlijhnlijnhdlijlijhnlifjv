// ============= src/types/oauth.types.ts =============

export interface OAuthClient {
  client_id: string;
  client_name: string;
  client_uri?: string;
  logo_uri?: string;
  redirect_uris: string[];
  scope: string;
}

export interface AuthorizationRequest {
  client_id: string;
  redirect_uri: string;
  response_type: 'code' | 'token';
  scope: string;
  state?: string;
  code_challenge?: string;
  code_challenge_method?: 'S256' | 'plain';
  nonce?: string;
  prompt?: 'none' | 'login' | 'consent' | 'select_account';
  max_age?: number;
}

export interface AuthorizationResponse {
  code?: string;
  state?: string;
  error?: string;
  error_description?: string;
}

export interface TokenRequest {
  grant_type: 'authorization_code' | 'refresh_token' | 'password';
  code?: string;
  redirect_uri?: string;
  code_verifier?: string;
  refresh_token?: string;
  username?: string;
  password?: string;
  client_id: string;
  client_secret?: string;
  scope?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  id_token?: string;
  scope?: string;
}

export interface UserInfo {
  sub: string;
  name?: string;
  preferred_username?: string;
  email?: string;
  email_verified?: boolean;
  picture?: string;
  updated_at?: number;
}