// frontend/src/components/CourseModal.tsx

import React, { useEffect, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import '../styles/CourseModal.scss';

interface ModalBlock {
  type: 'text' | 'image';
  content: string;
  order: number;
}

interface CourseModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  blocks: ModalBlock[];
  imageFormatter?: (url: string) => string;
}

const CourseModal: React.FC<CourseModalProps> = ({
  isOpen,
  onClose,
  title,
  blocks,
  imageFormatter = (url) => url
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Сортируем блоки по порядку
  const sortedBlocks = [...blocks].sort((a, b) => a.order - b.order);

  // Управление фокусом для accessibility
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
      document.body.style.overflow = 'hidden';
      document.body.classList.add('modal-open');
    }

    return () => {
      if (isOpen) {
        document.body.style.overflow = '';
        document.body.classList.remove('modal-open');
        previousActiveElement.current?.focus();
      }
    };
  }, [isOpen]);

  // Навигация с клавиатуры (только Escape для закрытия)
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, handleKeyDown]);

  // Закрытие по клику на backdrop
  const handleBackdropClick = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }, [onClose]);

  if (!isOpen) return null;

  const modalContent = (
    <div 
      className="course-modal-backdrop" 
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className="course-modal-container">
        <div 
          className="course-modal"
          ref={modalRef}
          tabIndex={-1}
          role="document"
        >
          {/* Header с заголовком и кнопкой закрытия */}
          <div className="modal-header">
            <div className="modal-title-wrapper">
              <h2 id="modal-title" className="modal-title">{title}</h2>
            </div>
            <button 
              className="modal-close"
              onClick={onClose}
              aria-label="Закрыть модальное окно"
              type="button"
            >
              <span className="material-symbols-rounded">close</span>
            </button>
          </div>

          {/* Разделитель */}
          <div className="modal-divider" />

          {/* Контент - простая прокручиваемая лента */}
          <div className="modal-content">
            {sortedBlocks.length === 0 ? (
              <div className="modal-empty">
                <span className="material-symbols-rounded">description</span>
                <p>Информация о программе курса будет доступна позже</p>
              </div>
            ) : (
              // Рендерим все блоки подряд
              sortedBlocks.map((block, index) => (
                <div key={index} className="modal-block">
                  {block.type === 'text' ? (
                    <div 
                      className="text-block"
                      dangerouslySetInnerHTML={{ 
                        __html: block.content 
                      }}
                    />
                  ) : (
                    <div className="image-block">
                      <img
                        src={imageFormatter(block.content)}
                        alt=""
                        loading="lazy"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

export default CourseModal;