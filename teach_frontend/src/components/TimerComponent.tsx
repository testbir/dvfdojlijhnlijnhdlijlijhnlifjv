// frontend/src/components/TimerComponent.tsx


import { useState, useEffect } from "react";

interface TimerComponentProps {
  initialSeconds: number;
  onExpire: () => void;
  onResend: () => void;
  canResend: boolean;
}

export default function TimerComponent({
  initialSeconds,
  onExpire,
  onResend,
  canResend,
}: TimerComponentProps) {
  const [seconds, setSeconds] = useState(initialSeconds);

  useEffect(() => {
    setSeconds(initialSeconds);
  }, [initialSeconds]);

  useEffect(() => {
    if (seconds <= 0) {
      onExpire();
      return;
    }

    const interval = setInterval(() => {
      setSeconds((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [seconds, onExpire]);

  const formatTime = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div style={{ textAlign: "center", marginTop: "20px" }}>
      {seconds > 0 ? (
        <p>Можно запросить повторно через {formatTime(seconds)}</p>
      ) : (
        <>
          <p>Код можно отправить повторно</p>
          <button
            onClick={onResend}
            disabled={!canResend}
            style={{
              marginTop: "10px",
              padding: "10px 20px",
              backgroundColor: canResend ? "#4CAF50" : "#ccc",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: canResend ? "pointer" : "not-allowed",
            }}
          >
            Повторно отправить код
          </button>
        </>
      )}
    </div>
  );
}