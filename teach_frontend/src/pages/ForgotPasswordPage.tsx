// src/pages/ForgotPasswordPage.tsx

import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import authService from "../services/authService";
import Layout from "../components/Layout";

import "../styles/auth.scss";
import "../styles/ForgotPasswordPage.scss";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    if (!error) return;
    const t = setTimeout(() => setError(""), 3000);
    return () => clearTimeout(t);
  }, [error]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      // новый сервис
      await authService.requestPasswordReset(email);
      navigate(
        `/email-verification?email=${encodeURIComponent(email)}&purpose=reset_password`
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.error ||
          err?.response?.data?.message ||
          "Пользователь с таким email не найден"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="auth-wrapper forgot-password-page">

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
              <h1 className="auth-title forgotpassword-title">Смена пароля</h1>

              <form onSubmit={handleSubmit} className="auth-form forgotpassword-form">
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

                <div className="auth-links forgotpassword-links">
                  <Link to="/login" className="forgotpassword-login-link">
                    Вернуться ко входу
                  </Link>
                </div>

                <div className="auth-error-container"></div>
                {error && <div className="auth-error forgotpassword-error">{error}</div>}

                <button type="submit" disabled={loading} className="auth-button forgotpassword-button">
                  {loading ? "Отправка..." : "Отправить код"}
                </button>
              </form>
            </div>
      </div>
    </Layout>
  );
}
