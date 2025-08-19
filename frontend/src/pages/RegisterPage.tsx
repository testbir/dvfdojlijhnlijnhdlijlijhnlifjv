// src/pages/RegisterPage.tsx

import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import authService from "../services/authService";
import Layout from "../components/Layout";
import authlogo from "../assets/authlogo.png";
import logomobile from "../assets/logomobile.png";

import "../styles/auth.scss";
import "../styles/RegisterPage.scss";

const errorTranslations: { [key: string]: string } = {
  "A user with that username already exists.": "Пользователь с таким логином уже существует.",
  "A user with that email already exists.": "Пользователь с такой почтой уже существует.",
  "This field may not be blank.": "Это поле не может быть пустым.",
  "Enter a valid email address.": "Введите корректный email адрес.",
  "This password is too short. It must contain at least 8 characters.": "Пароль слишком короткий. Минимум 8 символов.",
  "This password is too common.": "Пароль слишком простой.",
  "This password is entirely numeric.": "Пароль не может состоять только из цифр.",
  "Username may only contain letters, numbers and @/./+/-/_ characters.": "Логин может содержать только буквы, цифры и символы @/./+/-/_.",
};

const translateError = (error: string): string => errorTranslations[error] || error;

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password1: "",
    password2: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [canSubmit, setCanSubmit] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => setError(""), 3000);
    return () => clearTimeout(timer);
  }, [error]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    setCanSubmit(false);
    setError("");

    if (formData.password1 !== formData.password2) {
      setError("Пароли не совпадают");
      setCanSubmit(true);
      return;
    }

    setLoading(true);
    try {
        const res = await authService.register({
          username: formData.username.trim(),
          email: formData.email.trim(),
          password1: formData.password1,
          password2: formData.password2,
        });
      navigate(
        `/email-verification?user_id=${res.user_id}&email=${encodeURIComponent(
          formData.email
        )}&purpose=register`
      );
    } catch (err: any) {
      if (err.response?.status === 429) {
        setError("Слишком много попыток регистрации. Попробуйте через несколько минут.");
      } else {
        const data = err.response?.data;
        if (typeof data === "string") {
          setError(translateError(data));
        } else if (data && typeof data === "object") {
          const firstKey = Object.keys(data)[0];
          const firstValue = data[firstKey];
          const msg = Array.isArray(firstValue) ? firstValue[0] : firstValue;
          setError(translateError(String(msg)));
        } else {
          setError("Ошибка регистрации");
        }
      }
      setCanSubmit(false);
      setTimeout(() => setCanSubmit(true), 4000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="auth-wrapper register-page">
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
              <h1 className="auth-title register-title">Регистрация</h1>

              <form onSubmit={handleSubmit} className="auth-form register-form">
                <div className={`auth-input-wrapper ${formData.username ? "filled" : ""}`}>
                  <input
                    className="auth-input"
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    onFocus={(e) => e.target.parentElement?.classList.add("focused")}
                    onBlur={(e) => {
                      if (!e.target.value) e.target.parentElement?.classList.remove("focused");
                    }}
                    required
                  />
                  <span className="auth-placeholder">Введите логин</span>
                </div>

                <div className={`auth-input-wrapper ${formData.email ? "filled" : ""}`}>
                  <input
                    className="auth-input"
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    onFocus={(e) => e.target.parentElement?.classList.add("focused")}
                    onBlur={(e) => {
                      if (!e.target.value) e.target.parentElement?.classList.remove("focused");
                    }}
                    required
                  />
                  <span className="auth-placeholder">Введите почту</span>
                </div>

                <div className={`auth-input-wrapper ${formData.password1 ? "filled" : ""}`}>
                  <input
                    className="auth-input password-input"
                    type="password"
                    name="password1"
                    value={formData.password1}
                    onChange={handleChange}
                    onFocus={(e) => e.target.parentElement?.classList.add("focused")}
                    onBlur={(e) => {
                      if (!e.target.value) e.target.parentElement?.classList.remove("focused");
                    }}
                    required
                  />
                  <span className="auth-placeholder">Введите пароль</span>
                </div>

                <div className={`auth-input-wrapper ${formData.password2 ? "filled" : ""}`}>
                  <input
                    className="auth-input password-input"
                    type="password"
                    name="password2"
                    value={formData.password2}
                    onChange={handleChange}
                    onFocus={(e) => e.target.parentElement?.classList.add("focused")}
                    onBlur={(e) => {
                      if (!e.target.value) e.target.parentElement?.classList.remove("focused");
                    }}
                    required
                  />
                  <span className="auth-placeholder">Повторите пароль</span>
                </div>

                <div className="auth-links register-links">
                  <Link to="/login" className="register-login-link">
                    Уже есть аккаунт?
                  </Link>
                </div>

                <div className="auth-error-container"></div>
                {error && <div className="auth-error register-error">{error}</div>}

                <button type="submit" disabled={loading || !canSubmit} className="auth-button register-button">
                  {loading ? "Создание..." : "Создать профиль"}
                </button>

                <div className="register-terms">
                  Подтверждая, вы соглашаетесь с <Link to="/terms" className="terms-link">условиями</Link>.
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
