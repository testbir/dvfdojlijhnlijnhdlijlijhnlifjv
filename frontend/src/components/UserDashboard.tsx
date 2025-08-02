// src/components/UserDashboard.tsx

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import dashboardService, { type DashboardData, type UserData } from '../services/dashboardService';
import "../styles/UserDashboard.scss";

export default function UserDashboard() {
  const [isOpen, setIsOpen] = useState(false);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const { logout } = useAuth();

  // Загрузка базовых данных пользователя при монтировании
  useEffect(() => {
    let mounted = true; // Флаг для предотвращения race conditions
    
    const loadUserData = async () => {
      if (userData) return; // Если уже загружены, не загружаем повторно
      
      try {
        console.log('🔍 Загружаем данные пользователя...');
        const user = await dashboardService.getUserData();
        console.log('✅ Данные пользователя получены:', user);
        
        if (mounted) {
          setUserData(user);
        }
      } catch (err: any) {
        console.error('❌ Ошибка загрузки данных пользователя:', err);
        if (mounted) {
          setError('Ошибка загрузки профиля');
        }
      }
    };

    loadUserData();

    return () => {
      mounted = false; // Cleanup
    };
  }, []); // Пустой массив зависимостей - выполняется только при монтировании

  // Загрузка полных данных dashboard при открытии dropdown
  useEffect(() => {
    if (isOpen && !dashboardData) {
      loadDashboardData();
    }
  }, [isOpen]);

  // Закрытие dropdown при клике вне его
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError('');
    
    try {
      console.log('🔍 Загружаем полные данные dashboard...');
      const data = await dashboardService.getFullDashboard();
      console.log('✅ Данные dashboard получены:', data);
      
      setUserData(data.userData);
      setDashboardData(data.dashboardData);
    } catch (err: any) {
      console.error('❌ Ошибка загрузки dashboard:', err);
      setError('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      setIsOpen(false);
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  // Функция для закрытия дропдауна
  const handleClose = () => {
    setIsOpen(false);
  };

  // Дебаг информация
  console.log('🔄 UserDashboard render:', { 
    userData, 
    userDataExists: !!userData,
    username: userData?.username 
  });

  return (
    <div className="user-dashboard" ref={dropdownRef}>
      <button 
        className="dashboard-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <span className="material-symbols-rounded profile-icon">person</span>
        {/* Показываем реальный username или загрузку */}
        Мой Профиль
        <span className={`dropdown-arrow ${isOpen ? 'open' : ''}`}>▼</span>
      </button>

      {isOpen && (
        <div className="dashboard-dropdown">
          {loading ? (
            <div className="dashboard-loading">
              <div className="loading-spinner"></div>
              Загрузка...
            </div>
          ) : error ? (
            <div className="dashboard-error">
              <span className="error-icon">⚠️</span>
              {error}
              <button onClick={loadDashboardData} className="retry-btn">
                Повторить
              </button>
            </div>
          ) : (
            <>
              {/* Информация о пользователе */}
              <div className="dashboard-header">
                <div className="user-avatar">
                  <span className="material-symbols-rounded">person</span>
                </div>
                <div className="user-info">
                  {/* Показываем реальный username */}
                  <div className="username">{userData?.username || 'Загрузка...'}</div>
                  <div className="user-email">{userData?.email || 'Загрузка...'}</div>
                </div>
                {/* Кнопка закрытия для мобильной версии */}
                <button className="mobile-close-btn" onClick={handleClose}>
                  <span className="material-symbols-rounded">close</span>
                </button>
              </div>

              {/* Статистика */}
              {dashboardData && (
                <div className="dashboard-stats">
                  <div className="stat-item">
                    <span className="material-symbols-rounded">school</span>
                    <span>Курсов: {dashboardData.stats.total_courses}</span>
                  </div>
                  <div className="stat-item">
                    <span className="material-symbols-rounded">trending_up</span>
                    <span>Прогресс: {dashboardData.stats.total_progress_percent}%</span>
                  </div>
                </div>
              )}

              {/* Курсы */}
              {dashboardData && dashboardData.courses.length > 0 && (
                <div className="dashboard-courses">
                  <div className="courses-header">
                    <span className="material-symbols-rounded">book</span>
                    Мои курсы ({dashboardData.courses.length})
                  </div>
                  <div className="courses-list">
                    {dashboardData.courses.slice(0, 3).map((course) => (
                      <div key={course.course_id} className="course-item">
                        <div className="course-info">
                          <div className="course-title">{course.course_title}</div>
                          <div className="course-progress">
                            <div className="progress-bar">
                              <div 
                                className="progress-fill"
                                style={{ width: `${course.progress_percent}%` }}
                              ></div>
                            </div>
                            <span className="progress-text">{course.progress_percent}%</span>
                          </div>
                        </div>
                        {course.is_completed && (
                          <span className="completion-badge material-symbols-rounded">
                            check_circle
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Кнопка "Мои Курсы" - неактивная для новичков */}
              {(!dashboardData || dashboardData.courses.length === 0) && (
                <div className="dashboard-my-courses-section">
                  <button className="my-courses-btn-inactive" disabled>
                    <span className="material-symbols-outlined">stacks</span>
                    Мои Курсы
                  </button>
                  <div className="inactive-button-hint">
                    У вас пока нет приобретённых курсов
                  </div>
                </div>
              )}
              

              {/* Меню действий */}
              <div className="dashboard-actions">
                <button className="action-item">
                  <span className="material-symbols-rounded">settings</span>
                  Настройки
                </button>
                <button className="action-item logout-btn" onClick={handleLogout}>
                  <span className="material-symbols-rounded">logout</span>
                  Выйти
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}