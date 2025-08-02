// src/contexts/AuthContext.tsx

import React, { createContext, useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import authService from "../services/authService";
import type{ User } from "../types/auth.types";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const checkAuth = async () => {
    const tokens = authService.getTokens();
    if (!tokens) {
      setIsLoading(false);
      return;
    }

    try {
      // Здесь можно добавить запрос на получение данных пользователя
      // const response = await authApi.get("/api/user/me/");
      // setUser(response.data);
      setUser({ id: 1, email: "user@example.com", username: "user", is_email_confirmed: true });
    } catch (error) {
      authService.removeTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      await authService.login({ email, password });
      await checkAuth();
      navigate("/");
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    navigate("/");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};