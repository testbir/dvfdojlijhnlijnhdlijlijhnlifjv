// ============= src/utils/validators.ts =============

import { PASSWORD_MIN_LENGTH, USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH } from './constants';

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

export const validators = {
  email: (email: string): ValidationResult => {
    if (!email) {
      return { isValid: false, error: 'Email обязателен' };
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return { isValid: false, error: 'Неверный формат email' };
    }
    return { isValid: true };
  },

  username: (username: string): ValidationResult => {
    if (!username) {
      return { isValid: false, error: 'Имя пользователя обязательно' };
    }
    if (username.length < USERNAME_MIN_LENGTH) {
      return { isValid: false, error: `Минимум ${USERNAME_MIN_LENGTH} символа` };
    }
    if (username.length > USERNAME_MAX_LENGTH) {
      return { isValid: false, error: `Максимум ${USERNAME_MAX_LENGTH} символов` };
    }
    const usernameRegex = /^[a-zA-Z0-9_-]+$/;
    if (!usernameRegex.test(username)) {
      return { isValid: false, error: 'Только буквы, цифры, _ и -' };
    }
    return { isValid: true };
  },

  password: (password: string): ValidationResult => {
    if (!password) {
      return { isValid: false, error: 'Пароль обязателен' };
    }
    if (password.length < PASSWORD_MIN_LENGTH) {
      return { isValid: false, error: `Минимум ${PASSWORD_MIN_LENGTH} символов` };
    }
    return { isValid: true };
  },

  passwordConfirm: (password: string, confirmPassword: string): ValidationResult => {
    if (!confirmPassword) {
      return { isValid: false, error: 'Подтвердите пароль' };
    }
    if (password !== confirmPassword) {
      return { isValid: false, error: 'Пароли не совпадают' };
    }
    return { isValid: true };
  },

  code: (code: string): ValidationResult => {
    if (!code) {
      return { isValid: false, error: 'Код обязателен' };
    }
    if (!/^\d{6}$/.test(code)) {
      return { isValid: false, error: 'Код должен состоять из 6 цифр' };
    }
    return { isValid: true };
  },
};

export const getPasswordStrength = (password: string): {
  score: number;
  label: string;
  color: string;
} => {
  let score = 0;
  
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^a-zA-Z0-9]/.test(password)) score++;
  
  const strength = [
    { min: 0, label: 'Очень слабый', color: '#ff4444' },
    { min: 2, label: 'Слабый', color: '#ff8800' },
    { min: 3, label: 'Средний', color: '#ffbb00' },
    { min: 4, label: 'Хороший', color: '#88dd00' },
    { min: 5, label: 'Отличный', color: '#00cc00' },
  ];
  
  const result = strength.reverse().find(s => score >= s.min) || strength[0];
  
  return {
    score: Math.min(score / 6, 1),
    label: result.label,
    color: result.color,
  };
};