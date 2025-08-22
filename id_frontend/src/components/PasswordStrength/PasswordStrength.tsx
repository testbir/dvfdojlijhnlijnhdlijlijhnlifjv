// ============= src/components/PasswordStrength/PasswordStrength.tsx =============

import React, { useMemo } from 'react';
import { getPasswordStrength } from '../../utils/validators';
import './PasswordStrength.scss';

interface PasswordStrengthProps {
  password: string;
  showLabel?: boolean;
}

export const PasswordStrength: React.FC<PasswordStrengthProps> = ({ 
  password, 
  showLabel = true 
}) => {
  const strength = useMemo(() => getPasswordStrength(password), [password]);

  if (!password) return null;

  return (
    <div className="password-strength">
      <div className="password-strength__bars">
        <div 
          className="password-strength__bar"
          style={{
            width: `${strength.score * 100}%`,
            backgroundColor: strength.color
          }}
        />
      </div>
      {showLabel && (
        <span 
          className="password-strength__label"
          style={{ color: strength.color }}
        >
          {strength.label}
        </span>
      )}
    </div>
  );
};