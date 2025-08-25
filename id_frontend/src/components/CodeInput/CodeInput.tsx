// ============= src/components/CodeInput/CodeInput.tsx =============

import React, { useState, useRef, useEffect } from 'react';
interface CodeInputProps {
  length?: number;
  onChange: (code: string) => void;
  onComplete?: (code: string) => void;
  error?: boolean;
  disabled?: boolean;
  autoFocus?: boolean;
}

export const CodeInput: React.FC<CodeInputProps> = ({
  length = 4,
  onChange,
  onComplete,
  error = false,
  disabled = false,
  autoFocus = true,
}) => {
  const [values, setValues] = useState<string[]>(new Array(length).fill(''));
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (autoFocus && inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, [autoFocus]);

  const handleChange = (index: number, value: string) => {
    if (disabled) return;

    // Разрешаем только цифры
    const numericValue = value.replace(/[^0-9]/g, '');
    
    if (numericValue.length <= 1) {
      const newValues = [...values];
      newValues[index] = numericValue;
      setValues(newValues);
      
      const code = newValues.join('');
      onChange(code);
      
      // Переход к следующему полю
      if (numericValue && index < length - 1) {
        inputRefs.current[index + 1]?.focus();
      }
      
      // Вызываем onComplete если все поля заполнены
      if (code.length === length && onComplete) {
        onComplete(code);
      }
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (disabled) return;

    if (e.key === 'Backspace' && !values[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    if (disabled) return;
    
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text/plain').replace(/[^0-9]/g, '').slice(0, length);
    const newValues = [...values];
    
    for (let i = 0; i < pastedData.length; i++) {
      newValues[i] = pastedData[i];
    }
    
    setValues(newValues);
    const code = newValues.join('');
    onChange(code);
    
    // Фокус на последнее заполненное поле или следующее пустое
    const lastFilledIndex = Math.min(pastedData.length - 1, length - 1);
    inputRefs.current[lastFilledIndex]?.focus();
    
    if (code.length === length && onComplete) {
      onComplete(code);
    }
  };

  return (
    <div className={`code-input ${error ? 'code-input--error' : ''} ${disabled ? 'code-input--disabled' : ''}`}>
      {values.map((value, index) => (
        <input
          key={index}
          ref={(el) => { inputRefs.current[index] = el; }}  
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={value}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          onPaste={handlePaste}
          disabled={disabled}
          className="code-input__field"
          autoComplete="off"
        />
      ))}
    </div>
  );
};