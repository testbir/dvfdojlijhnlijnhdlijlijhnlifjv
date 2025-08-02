// src/pages/ForgotPasswordPage.tsx

import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import authService from "../services/authService";
import Layout from "../components/Layout";
import authlogo from "../assets/authlogo.png";
import logomobile from "../assets/logomobile.png";

// Импорт стилей
import "../styles/auth.scss"
import "../styles/ForgotPasswordPage.scss"

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  // Автоматически скрываем ошибку через 3 секунды
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError("");
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await authService.requestPasswordReset({ email });
      navigate(`/email-verification?email=${encodeURIComponent(email)}&purpose=reset_password`);
    } catch (err: any) {
      setError(err.response?.data?.error || "Пользователь с таким email не найден");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="auth-wrapper forgot-password-page">
        <div className="auth-box">
          {/* Левая сторона (логотип) - показывается только на десктопе */}
          <div className="auth-side auth-side--left">
            {/* Кнопка прижата к верху */}
            <Link to="/" className="auth-back">
              <span className="material-symbols-outlined icon-back" aria-hidden="true" role="presentation">
                arrow_back
              </span>
              На Главную
            </Link>

            {/* Контейнер логотипа — по центру блока */}
            <div className="auth-logo-container">
              <div className="auth-logo">
                <img src={authlogo} alt="AsyncTeach" />
              </div>
            </div>
          </div>

          {/* Правая сторона (форма восстановления) */}
          <div className="auth-side auth-side--right">

            {/* Мобильный логотип */}
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
              <h1 className="auth-title forgotpassword-title">Восстановление пароля</h1>

              {/* Форма восстановления пароля */}
              <form onSubmit={handleSubmit} className="auth-form forgotpassword-form">
                {/* Поле ввода электронной почты */}
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

                {/* Дополнительные ссылки */}
                <div className="auth-links forgotpassword-links">
                  <Link to="/login" className="forgotpassword-login-link">
                    Вернуться ко входу
                  </Link>
                </div>

                {/* Блок вывода ошибок */}
                <div className="auth-error-container"></div>
                {error && <div className="auth-error forgotpassword-error">{error}</div>}

                {/* Кнопка отправки */}
                <button
                  type="submit"
                  disabled={loading}
                  className="auth-button forgotpassword-button"
                >
                  {loading ? "Отправка..." : "Отправить код"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}