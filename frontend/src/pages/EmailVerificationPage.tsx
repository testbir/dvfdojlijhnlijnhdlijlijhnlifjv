// frontend/src/pages/EmailVerificationPage.tsx

import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import authService from "../services/authService";

const EmailVerificationPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [resendTimer, setResendTimer] = useState(0);

  // Получаем данные из состояния навигации
  const userId = location.state?.userId;
  const email = location.state?.email;
  const message = location.state?.message;

  useEffect(() => {
    // Если нет userId, перенаправляем на регистрацию
    if (!userId) {
      navigate("/register");
    }
  }, [userId, navigate]);

  useEffect(() => {
    // Таймер для повторной отправки
    if (resendTimer > 0) {
      const timer = setTimeout(() => setResendTimer(resendTimer - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendTimer]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await authService.verifyCode(userId, code);
      // После успешной верификации перенаправляем на главную
      navigate("/", { 
        state: { message: "Email успешно подтвержден!" } 
      });
    } catch (error: any) {
      if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else {
        setError("Неверный код подтверждения");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    setResending(true);
    setError("");

    try {
      await authService.resendCode(userId, 'register');
      setResendTimer(60); // 60 секунд до следующей отправки
    } catch (error: any) {
      if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else {
        setError("Не удалось отправить код");
      }
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Подтверждение Email
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {message || `Мы отправили 4-значный код на ${email || "ваш email"}`}
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div>
            <label htmlFor="code" className="block text-sm font-medium text-gray-700">
              Код подтверждения
            </label>
            <input
              id="code"
              name="code"
              type="text"
              autoComplete="one-time-code"
              required
              maxLength={4}
              pattern="[0-9]{4}"
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm text-center text-2xl"
              placeholder="0000"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 4))}
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || code.length !== 4}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Проверка..." : "Подтвердить"}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={handleResendCode}
              disabled={resending || resendTimer > 0}
              className="text-sm text-indigo-600 hover:text-indigo-500 disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              {resendTimer > 0 
                ? `Отправить повторно через ${resendTimer}с` 
                : "Отправить код повторно"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EmailVerificationPage;