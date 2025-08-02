// src/api/authApi.ts

import api from './axiosInstance';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const login = async (
  username: string,
  password: string
): Promise<LoginResponse> => {
  const response = await api.post(
    '/auth/login',
    { username, password },
    {
      headers: {
        'Content-Type': 'application/json', // ← критично важно
      },
    }
  );

  return response.data;
};
