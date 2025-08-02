// src/pages/LoginPage.tsx

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import Layout from "../components/Layout";
import authlogo from "../assets/authlogo.png";
import logomobile from "../assets/logomobile.png";

// Импорт стилей для страницы авторизации
import "../styles/auth.scss"
import "../styles/LoginPage.scss"

export default function LoginPage() {
  // Состояния для управления формой входа
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [activationData, setActivationData] = useState<{
    user_id: number;
    email: string;
  } | null>(null);
  
  // Получение функции входа из хука аутентификации и навигации
  const { login } = useAuth();
  const navigate = useNavigate();

  // Обработчик отправки формы входа
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setActivationData(null);
    setLoading(true);

    try {
      await login(email, password);
      navigate("/");
      
    } catch (err: any) {
      const errorData = err.response?.data;
      
      // Проверяем специальную ошибку активации
      if (errorData?.error === 'account_not_activated') {
        setError(errorData.message);
        setActivationData({
          user_id: errorData.user_id,
          email: errorData.email
        });
      } else {
        setError(errorData?.detail || errorData?.message || "Неверные учетные данные");
      }
    } finally {
      setLoading(false);
    }
  };

  // Переход на страницу активации
  const goToActivation = () => {
    if (activationData) {
      navigate(`/email-verification?user_id=${activationData.user_id}&email=${encodeURIComponent(activationData.email)}&purpose=register`);
    }
  };

  // Рендеринг страницы входа
  return (
    <Layout>
      <div className="auth-wrapper login-page">
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

          {/* Правая сторона (форма входа) */}
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

              {/* Форма входа */}
              <form onSubmit={handleSubmit} className="auth-form login-form">
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

                {/* Поле ввода пароля */}
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

                {/* Дополнительные ссылки */}
                <div className="auth-links login-links">
                  <Link to="/register" className="login-register-link">
                    Создать аккаунт
                  </Link>
                  <Link to="/forgot-password" className="login-forgot-link">
                    Забыли пароль?
                  </Link>
                </div>

                {/* Блок вывода ошибок */}

                <div className="auth-error-container"></div>
                {error && (
                  <div className="auth-error login-error">
                    <span>{error}</span>
                    {/* Кнопка активации для неактивированных пользователей */}
                    {activationData && (
                      <button 
                        type="button"
                        onClick={goToActivation}
                        className="activation-btn"
                      >
                        Активировать
                      </button>
                    )}
                  </div>
                )}

                {/* Кнопка входа */}
                <button
                  type="submit"
                  disabled={loading}
                  className="auth-button login-button"
                >
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