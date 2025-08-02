// src/components/loading/AuthLoading.tsx

import React from "react";
import "./AuthLoading.scss";

// Спиннер для кнопок
export const ButtonSpinner: React.FC<{ size?: "small" | "medium" }> = ({ 
  size = "medium" 
}) => (
  <div className={`button-spinner ${size}`}>
    <div className="spinner"></div>
  </div>
);

// Overlay спиннер для критических операций
export const AuthOverlay: React.FC<{ 
  message?: string;
  children?: React.ReactNode;
}> = ({ 
  message = "Загрузка...", 
  children 
}) => (
  <div className="auth-overlay">
    <div className="auth-overlay-content">
      <div className="auth-overlay-spinner">
        <div className="spinner"></div>
      </div>
      {children || <p className="auth-overlay-message">{message}</p>}
    </div>
  </div>
);

// Inline спиннер для текста
export const InlineSpinner: React.FC<{ 
  message?: string;
  size?: "small" | "medium";
}> = ({ 
  message = "Отправка...", 
  size = "small" 
}) => (
  <div className="inline-spinner">
    <div className={`spinner ${size}`}></div>
    <span className="inline-spinner-text">{message}</span>
  </div>
);

// Спиннер для таймера (например, для повторной отправки кода)
export const TimerSpinner: React.FC<{ 
  seconds: number;
  message?: string;
}> = ({ 
  seconds, 
  message = "Можно запросить повторно через" 
}) => (
  <div className="timer-spinner">
    <div className="timer-icon">
      <div className="spinner small"></div>
    </div>
    <span className="timer-text">
      {message} {seconds} сек.
    </span>
  </div>
);

export default {
  ButtonSpinner,
  AuthOverlay,
  InlineSpinner,
  TimerSpinner,
};