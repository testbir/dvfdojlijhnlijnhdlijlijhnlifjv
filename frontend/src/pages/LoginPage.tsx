// src/pages/LoginPage.tsx

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import Layout from "../components/Layout";
import authlogo from "../assets/authlogo.png";
import logomobile from "../assets/logomobile.png";

import "../styles/auth.scss";
import "../styles/LoginPage.scss";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [activationData, setActivationData] = useState<{ user_id: number; email: string } | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setActivationData(null);
    setLoading(true);

    try {
      await login(email.trim(), password);
      navigate("/");
    } catch (err: any) {
      // Новый формат специальной ошибки из authService.login
      if (err?.type === "NOT_ACTIVATED") {
        setError(err.message || "Аккаунт не активирован");
        setActivationData({ user_id: err.userId, email: err.email });
      } else {
        const data = err?.response?.data;
        setError(data?.detail || data?.message || err?.message || "Неверные учетные данные");
      }
    } finally {
      setLoading(false);
    }
  };

  const goToActivation = () => {
    if (!activationData) return;
    navigate(
      `/email-verification?user_id=${activationData.user_id}&email=${encodeURIComponent(
        activationData.email
      )}&purpose=register`
    );
  };

  return (
    <Layout>
      <div className="auth-wrapper login-page">
        <div className="auth-box">
          <div className="auth-side auth-side--left">
            <Link to="/" className="auth-back">
              <span className="material-symbols-outlined icon-back" aria-hidden="true" role="presentation">
                arrow_back
              </span>
              На Главную
            </Link>

            <div className="auth-logo-container">
              <div className="auth-logo">
                <img src={authlogo} alt="AsyncTeach" />
              </div>
            </div>
          </div>

          <div className="auth-side auth-side--right">
            <div className="mobile-logo-container">
              <Link to="/" className="mobile-auth-back">
                <span className="material-symbols-outlined icon-back" aria-hidden="true" role="presentation">
                  arrow_back
                </span>
                На Главную
              </Link>

              <div className="mobile-logo">
                <img src={logomobile} alt="AsyncTeach" />
              </div>
            </div>

            <div className="auth-content">
              <h1 className="auth-title login-title">Вход</h1>

              <form onSubmit={handleSubmit} className="auth-form login-form">
                <div className={`auth-input-wrapper ${email ? "filled" : ""}`}>
                  <input
                    className="auth-input"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onFocus={(e) => e.target.parentElement?.classList.add("focused")}
                    onBlur={(e) => {
                      if (!e.target.value) e.target.parentElement?.classList.remove("focused");
                    }}
                    required
                  />
                  <span className="auth-placeholder">Введите почту</span>
                </div>

                <div className={`auth-input-wrapper ${password ? "filled" : ""}`}>
                  <input
                    className="auth-input password-input"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={(e) => e.target.parentElement?.classList.add("focused")}
                    onBlur={(e) => {
                      if (!e.target.value) e.target.parentElement?.classList.remove("focused");
                    }}
                    required
                  />
                  <span className="auth-placeholder">Введите пароль</span>
                </div>

                <div className="auth-links login-links">
                  <Link to="/register" className="login-register-link">
                    Создать аккаунт
                  </Link>
                  <Link to="/forgot-password" className="login-forgot-link">
                    Забыли пароль?
                  </Link>
                </div>

                <div className="auth-error-container"></div>
                {error && (
                  <div className="auth-error login-error">
                    <span>{error}</span>
                    {activationData && (
                      <button type="button" onClick={goToActivation} className="activation-btn">
                        Активировать
                      </button>
                    )}
                  </div>
                )}

                <button type="submit" disabled={loading} className="auth-button login-button">
                  {loading ? "Вход..." : "Войти"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
