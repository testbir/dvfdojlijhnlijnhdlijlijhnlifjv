// ============= src/components/LoadingOverlay/LoadingOverlay.tsx =============

import React from 'react';

interface LoadingOverlayProps {
  message?: string;
  fullScreen?: boolean;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  message = 'Загрузка...', 
  fullScreen = true 
}) => {
  return (
    <div className={`loading-overlay ${fullScreen ? 'loading-overlay--fullscreen' : ''}`}>
      <div className="loading-overlay__content">
        <div className="loading-overlay__spinner" />
        {message && <p className="loading-overlay__message">{message}</p>}
      </div>
    </div>
  );
};