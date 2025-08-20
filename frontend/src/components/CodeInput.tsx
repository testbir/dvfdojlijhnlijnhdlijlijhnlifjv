// frontend/src/components/CodeInput.tsx

import React, { useRef, useState, useEffect } from "react";
import "../styles/EmailVerificationPage.scss"

interface CodeInputProps {
  length?: number;
  onComplete: (code: string) => void;
  disabled?: boolean;
}

export default function CodeInput({ length = 4, onComplete, disabled = false }: CodeInputProps) {
  const [values, setValues] = useState<string[]>(Array(length).fill(""));
  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    const code = values.join("");
    if (code.length === length && code.match(/^\d+$/)) {
      onComplete(code);
    }
  }, [values, length, onComplete]);

  const handleChange = (index: number, value: string) => {
    if (value.match(/[^0-9]/)) return;

    const newValues = [...values];
    newValues[index] = value.slice(-1);
    setValues(newValues);

    if (value && index < length - 1) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !values[index] && index > 0) {
      inputsRef.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").slice(0, length);
    
    if (pastedData.match(/^\d+$/)) {
      const newValues = pastedData.split("").concat(Array(length).fill("")).slice(0, length);
      setValues(newValues);
      inputsRef.current[Math.min(pastedData.length, length - 1)]?.focus();
    }
  };

  return (
    <div className="code-input-container">
      {values.map((value, index) => (
        <input
          key={index}
          ref={(el) => {
            inputsRef.current[index] = el;
          }}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={value}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          onPaste={handlePaste}
          disabled={disabled}
          className={`code-input-field ${value ? 'filled' : ''}`}
        />
      ))}
    </div>
  );
}