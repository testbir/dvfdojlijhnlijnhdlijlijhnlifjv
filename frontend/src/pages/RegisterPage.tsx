// src/pages/RegisterPage.tsx

import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import authService from "../services/authService";
import Layout from "../components/Layout";

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

                                <div className="register-terms">
                  Подтверждая, вы соглашаетесь с <Link to="/terms" className="terms-link">условиями</Link>.
                </div>

                <button type="submit" disabled={loading || !canSubmit} className="auth-button register-button">
                  {loading ? "Создание..." : "Создать профиль"}
                </button>
              </form>
            </div>
          </div>
    </Layout>
  );
}
