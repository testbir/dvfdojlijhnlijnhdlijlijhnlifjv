// ============= src/components/Layout/Layout.tsx =============

import React from 'react';
import './Layout.scss';

interface LayoutProps {
  children: React.ReactNode;
  showLogo?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({ children, showLogo = true }) => {
  return (
    <div className="layout">
      <div className="layout-background" />
      <div className="layout-container">
        {showLogo && (
          <div className="id-badge">
            <div className="id-icon">
              <svg width="23" height="22" viewBox="0 0 23 22" xmlns="http://www.w3.org/2000/svg">
                <path d="M16.4131 19.3398L12.4463 13.0098L12.082 12.4287L11.6406 12.9531L7.85742 17.4482L7.73926 17.5879V20.9697H3.66211L4.19629 16.7354L9.09277 11.2275L9.51465 10.7539L8.95605 10.4541L5.6875 8.70312L5.65234 8.68359L5.61523 8.6709L2.07422 7.44922L21.7803 1.28809L16.4131 19.3398Z" 
                      fill="#69A2FF" stroke="#69A2FF"/>
              </svg>
            </div>
            <span className="id-text">ID</span>
          </div>
        )}
        
        <div className="layout-content">
          {children}
        </div>
      </div>
    </div>
  );
};