// src/pages/LoginPage.tsx

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import Layout from "../components/Layout";



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

        <div className="id-badge">
            <div className="id-icon">
              <svg width="23" height="22" viewBox="0 0 23 22" xmlns="http://www.w3.org/2000/svg">
                <path d="M16.4131 19.3398L12.4463 13.0098L12.082 12.4287L11.6406 12.9531L7.85742 17.4482L7.73926 17.5879V20.9697H3.66211L4.19629 16.7354L9.09277 11.2275L9.51465 10.7539L8.95605 10.4541L5.6875 8.70312L5.65234 8.68359L5.61523 8.6709L2.07422 7.44922L21.7803 1.28809L16.4131 19.3398Z" fill="#69A2FF" stroke="#69A2FF"/>
              </svg>
            </div>
            <span className="id-text">ID</span>
          </div>

          <div className="logout-btn">
            <span className="material-symbols-outlined">close</span>
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
    </Layout>
  );
}
