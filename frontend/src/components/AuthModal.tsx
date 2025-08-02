// src/components/AuthModal.tsx

import React from 'react';
import '../styles/AuthModal.scss';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRegister: () => void;
  onLogin: () => void;
  courseTitle?: string;
  coursePrice?: number;
}

export default function AuthModal({ 
  isOpen, 
  onClose, 
  onRegister, 
  onLogin, 
  courseTitle, 
  coursePrice 
}: AuthModalProps) {
  
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="auth-modal-overlay" onClick={handleBackdropClick}>
      <div className="auth-modal">
        <div className="auth-modal-header">
          <button className="auth-modal-close" onClick={onClose}>
            <span className="material-symbols-rounded">close</span>
          </button>
        </div>

        <div className="auth-modal-content">
          <div className="auth-modal-icon">
            <span className="material-symbols-rounded">school</span>
          </div>
          
          <h2 className="auth-modal-title">Получите доступ к курсу</h2>
          
          {courseTitle && (
            <div className="auth-modal-course-info">
              <div className="course-highlight">
                <span className="course-name">{courseTitle}</span>
                {coursePrice && (
                  <span className="course-price">{coursePrice} ₽</span>
                )}
              </div>
            </div>
          )}

          <p className="auth-modal-description">
            Войдите в аккаунт или создайте новый, чтобы приобрести курс
          </p>

          <div className="auth-modal-actions">
            <button 
              className="auth-modal-btn auth-modal-btn--primary"
              onClick={onRegister}
            >
              <span className="material-symbols-rounded">person_add</span>
              Создать аккаунт
            </button>
            
            <button 
              className="auth-modal-btn auth-modal-btn--secondary"
              onClick={onLogin}
            >
              <span className="material-symbols-rounded">login</span>
              Войти в аккаунт
            </button>
          </div>

          <div className="auth-modal-benefits">
            <div className="benefit-item">
              <span className="material-symbols-rounded">check_circle</span>
              <span>Пожизненный доступ</span>
            </div>
            <div className="benefit-item">
              <span className="material-symbols-rounded">check_circle</span>
              <span>Отслеживание прогресса</span>
            </div>
            <div className="benefit-item">
              <span className="material-symbols-rounded">check_circle</span>
              <span>Практические задания</span>
            </div>
          </div>

          <div className="auth-modal-footer">
            <span className="footer-text">
              Регистрация займет меньше минуты
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}