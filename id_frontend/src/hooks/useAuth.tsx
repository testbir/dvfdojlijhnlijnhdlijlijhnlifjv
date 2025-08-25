// ============= src/hooks/useAuth.tsx =============

import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authService } from '../services/auth.service';
import { storageService } from '../services/storage.service';
import { type User } from '../types/auth.types';
import { TOKEN_STORAGE_KEY, REFRESH_TOKEN_STORAGE_KEY, ID_TOKEN_STORAGE_KEY } from '../utils/constants'

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, passwordConfirm: string) => Promise<{ userId: string; email: string }>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

const checkAuth = async () => {
  setIsLoading(true)
  try {
    const userData = await authService.getCurrentUser() // по cookie или по Bearer
    setUser(userData)
  } catch {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
    localStorage.removeItem(ID_TOKEN_STORAGE_KEY)
    setUser(null)
  } finally {
    setIsLoading(false)
  }
}

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login({ email, password });
    setUser(response.user);
  };

  const register = async (username: string, email: string, password: string, passwordConfirm: string) => {
    const response = await authService.register({
      username,
      email,
      password,
      password_confirm: passwordConfirm,
    });
    return { userId: response.user_id, email: response.email };
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    storageService.clear();
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};