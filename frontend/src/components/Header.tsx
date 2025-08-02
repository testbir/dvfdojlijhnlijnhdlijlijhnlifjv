// src/components/Header.tsx

import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import logo from "../assets/logo.png";
import "../styles/Header.scss";
import UserDashboard from "./UserDashboard";

export default function Header({
  searchQuery,
  setSearchQuery,
}: {
  searchQuery?: string;
  setSearchQuery?: (value: string) => void;
}) {
  const location = useLocation();
  const currentPath = location.pathname;
  const { isAuthenticated } = useAuth();

  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="header-logo-link">
          <img src={logo} alt="Логотип" className="logo" />
        </Link>

        <div className="header-right">
          <div className="search-block">
            <input
              type="text"
              placeholder="Поиск курсов..."
              className="search-input"
              value={searchQuery || ""}
              onChange={(e) => setSearchQuery?.(e.target.value)}
            />
          </div>

            {isAuthenticated ? (
            <UserDashboard />
            ) : (
            <div className="auth-buttons">
              <Link to={`/login?redirect=${currentPath}`} className="header-auth-button">
                Вход
              </Link>
              <Link to={`/register?redirect=${currentPath}`} className="header-auth-button">
                Регистрация
              </Link>
            </div>
          )}


        </div>
      </div>
    </header>
  );
}