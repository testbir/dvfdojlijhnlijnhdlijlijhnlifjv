// src/pages/PasswordResetSuccessPage.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';

const PasswordResetSuccessPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="page reset-success">
      <h2>Пароль успешно обновлён</h2>
      <p>Теперь вы можете войти в систему с новым паролем.</p>
      <button onClick={() => navigate('/login')}>
        Перейти ко входу
      </button>
    </div>
  );
};

export default PasswordResetSuccessPage;
