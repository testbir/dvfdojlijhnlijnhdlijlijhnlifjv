// src/pages/SetNewPasswordPage.tsx

import React, { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Layout from "../components/Layout";
import authlogo from "../assets/authlogo.png";
import logomobile from "../assets/logomobile.png";
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
        <div className="auth-box">
          <div className="auth-side auth-side--left">
            <div className="auth-logo-container">
              <div className="auth-logo">
                <img src={authlogo} alt="AsyncTeach" />
              </div>
            </div>
          </div>

          <div className="auth-side auth-side--right">
            <div className="auth-mobile-logo">
              <img src={logomobile} alt="AsyncTeach" />
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
        </div>
      </div>
    </Layout>
  );
};

export default SetNewPasswordPage;
