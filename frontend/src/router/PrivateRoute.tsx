// src/router/PrivateRoute.tsx

import React from "react";
import { Navigate } from "react-router-dom";

// Вариант без контекста — только по наличию access токена
const isAuthenticated = () => {
  return !!localStorage.getItem("access"); // или sessionStorage
};

interface Props {
  children: React.ReactNode;
}

const PrivateRoute: React.FC<Props> = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default PrivateRoute;
