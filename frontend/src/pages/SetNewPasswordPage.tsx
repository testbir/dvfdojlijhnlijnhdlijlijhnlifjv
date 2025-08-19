// src/pages/SetNewPasswordPage.tsx

import React, { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Layout from "../components/Layout";
import authService from "../services/authService";

import "../styles/auth.scss";
import "../styles/SetNewPasswordPage.scss";

const SetNewPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const userId = searchParams.get("user_id");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!userId) {
      setError("Отсутствует user_id");
      return;
    }
    if (password1 !== password2) {
      setError("Пароли не совпадают");
      return;
    }

    setLoading(true);
    try {
      await authService.setNewPassword(Number(userId), password1);
      navigate("/login");
    } catch (err: any) {
      setError(err?.response?.data?.error || err?.message || "Ошибка при обновлении пароля");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="auth-wrapper">

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
              <h1 className="auth-title newpassword-title">Новый пароль</h1>

              <form onSubmit={handleSubmit} className="auth-form newpassword-form">
                <div className={`auth-input-wrapper ${password1 ? "filled" : ""}`}>
                  <input
                    className="auth-input password-input"
                    type="password"
                    value={password1}
                    onChange={(e) => setPassword1(e.target.value)}
                    onFocus={(e) => e.target.parentElement?.classList.add("focused")}
                    onBlur={(e) => {
                      if (!e.target.value) e.target.parentElement?.classList.remove("focused");
                    }}
                    required
                  />
                  <span className="auth-placeholder">Новый пароль</span>
                </div>

                <div className={`auth-input-wrapper ${password2 ? "filled" : ""}`}>
                  <input
                    className="auth-input password-input"
                    type="password"
                    value={password2}
                    onChange={(e) => setPassword2(e.target.value)}
                    onFocus={(e) => e.target.parentElement?.classList.add("focused")}
                    onBlur={(e) => {
                      if (!e.target.value) e.target.parentElement?.classList.remove("focused");
                    }}
                    required
                  />
                  <span className="auth-placeholder">Повторите пароль</span>
                </div>

                {error && <div className="auth-error newpassword-error">{error}</div>}

                <button type="submit" disabled={loading} className="auth-button newpassword-button">
                  {loading ? "Сохранение..." : "Сменить пароль"}
                </button>
              </form>
            </div>
          </div>
    </Layout>
  );
};

export default SetNewPasswordPage;
