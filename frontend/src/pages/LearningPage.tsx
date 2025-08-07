// frontend/src/pages/LearningPage.tsx


import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DOMPurify from 'dompurify';
import { learningService } from '../services/learningService';
import '../styles/LearningPage.scss';

import 'prismjs/plugins/line-numbers/prism-line-numbers.css';
import 'prismjs/plugins/line-numbers/prism-line-numbers';
import Prism from 'prismjs';
import 'prism-themes/themes/prism-vsc-dark-plus.css';
import 'prismjs/components/prism-python';   //  ⬅️ добавили

// нужные языки
import 'prismjs/components/prism-markup';   // html / xml

interface Module {
  id: string;
  title: string;
  groupId: string;
  order: number;
}

interface Group {
  id: string;
  title: string;
  order: number;
}

interface ContentBlock {
  id: string;
  type: 'text' | 'code' | 'video' | 'image';
  title: string;
  content: string;
  order: number;
}

interface CourseData {
  id: string;
  title: string;
  groups: Group[];
  modules: Module[];
  progress: number;
}



const LearningPage: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  
  const [courseData, setCourseData] = useState<CourseData | null>(null);
  const [selectedModule, setSelectedModule] = useState<string>('');
  const [moduleContent, setModuleContent] = useState<ContentBlock[]>([]);
  const [isMenuCollapsed, setIsMenuCollapsed] = useState(false);
  const [isProgressBarVisible, setIsProgressBarVisible] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedCodeId, setCopiedCodeId] = useState<string | null>(null);


  useEffect(() => {
    loadCourseData();
  }, [courseId]);

  useEffect(() => {
    if (selectedModule) {
      loadModuleContent(selectedModule);
    }
  }, [selectedModule]);

  // ⬇️ сразу после import-ов и остальных useEffect-ов
useEffect(() => {
  Prism.highlightAll();          // раскрашивает + вешает line-numbers
}, [moduleContent]);              // вызываем каждый раз, когда загрузился новый блок


  const loadCourseData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Проверяем доступ к курсу
      const hasAccess = await learningService.checkCourseAccess(courseId!);
      if (!hasAccess) {
        setError('У вас нет доступа к этому курсу');
        return;
      }

      const data = await learningService.getCourseData(courseId!);
      setCourseData(data);
      
      // Раскрываем все группы по умолчанию
      setExpandedGroups(new Set(data.groups.map(g => g.id)));
      
      // Выбираем первый модуль
      if (data.modules.length > 0) {
        const firstModule = data.modules.sort((a, b) => a.order - b.order)[0];
        setSelectedModule(firstModule.id);
      }
    } catch (error) {
      setError('Не удалось загрузить данные курса');
      console.error('Error loading course data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadModuleContent = async (moduleId: string) => {
    try {
      const content = await learningService.getModuleContent(courseId!, moduleId);
      // Сортируем контент по order
      const sortedContent = content.sort((a, b) => a.order - b.order);
      setModuleContent(sortedContent);
    } catch (error) {
      console.error('Error loading module content:', error);
    }
  };

  const toggleGroup = useCallback((groupId: string) => {
    setExpandedGroups(prev => {
      const newExpanded = new Set(prev);
      if (newExpanded.has(groupId)) {
        newExpanded.delete(groupId);
      } else {
        newExpanded.add(groupId);
      }
      return newExpanded;
    });
  }, []);

  const handleModuleClick = useCallback((moduleId: string) => {
    setSelectedModule(moduleId);
  }, []);

  const toggleMenu = useCallback(() => {
    setIsMenuCollapsed(prev => !prev);
  }, []);

  const toggleProgressBar = useCallback(() => {
    setIsProgressBarVisible(prev => !prev);
  }, []);

  const handleCopyCode = useCallback((blockId: string, code: string) => {
    navigator.clipboard.writeText(code).then(() => {
      setCopiedCodeId(blockId);
      setTimeout(() => setCopiedCodeId(null), 2000);
    });
  }, []);

  const handleCompleteModule = useCallback(async () => {
    if (!selectedModule || !courseId) return;
    
    try {
      await learningService.markModuleCompleted(courseId, selectedModule);
      
      // Находим следующий модуль
      const currentIndex = courseData?.modules.findIndex(m => m.id === selectedModule);
      if (currentIndex !== undefined && currentIndex < (courseData?.modules.length || 0) - 1) {
        const nextModule = courseData?.modules[currentIndex + 1];
        if (nextModule) {
          setSelectedModule(nextModule.id);
        }
      }
      
      // Обновляем прогресс
      await loadCourseData();
    } catch (error) {
      console.error('Error completing module:', error);
    }
  }, [selectedModule, courseId, courseData]);

  const renderContentBlock = useCallback((block: ContentBlock) => {
    switch (block.type) {
      case 'text':
        return (
          <div 
            className="content-text" 
            dangerouslySetInnerHTML={{ 
              __html: DOMPurify.sanitize(block.content) 
            }} 
          />
        );
      
case 'code': {
  const lang = 'python';            // или вычисляй динамически

  return (
    <div className="content-code-wrapper">
      <pre className="content-code line-numbers">
        <code className={`language-${lang}`}>
          {block.content}         {/* сырой текст кода, БЕЗ Prism.highlight */}
        </code>
      </pre>

      <button
        className={`copy-button ${copiedCodeId === block.id ? 'copied' : ''}`}
        onClick={() => handleCopyCode(block.id, block.content)}
      >
        <span className="material-symbols-outlined">
          {copiedCodeId === block.id ? 'check' : 'content_copy'}
        </span>
        <span className="copy-text">
          {copiedCodeId === block.id ? 'Copied!' : 'Copy Code'}
        </span>
      </button>
    </div>
  );
}


      
      case 'video':
        return (
          <div className="content-video">
            <video controls src={block.content} />
          </div>
        );
      
      case 'image':
        return (
          <div className="content-image">
            <img src={block.content} alt={block.title} />
          </div>
        );
      
      default:
        return null;
    }
  }, [copiedCodeId, handleCopyCode]);

  const sortedGroups = useMemo(() => {
    return courseData?.groups.sort((a, b) => a.order - b.order) || [];
  }, [courseData?.groups]);

  const getModulesForGroup = useCallback((groupId: string) => {
    return courseData?.modules
      .filter(module => module.groupId === groupId)
      .sort((a, b) => a.order - b.order) || [];
  }, [courseData?.modules]);

  if (isLoading) {
    return (
      <div className="learning-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <span>Загрузка курса...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="learning-page">
        <div className="error-container">
          <h2>Ошибка</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')}>Вернуться на главную</button>
        </div>
      </div>
    );
  }

  if (!courseData) {
    return null;
  }

  const currentModule = courseData.modules.find(m => m.id === selectedModule);

  return (
    <div className="learning-page">
      <div className="glass-container">
        {/* Левое меню */}
        <aside className={`left-menu ${isMenuCollapsed ? 'collapsed' : ''}`}>
          <div className="menu-controls">
            <button 
              className="icon-button toolbar-button"
              onClick={toggleProgressBar}
              title="Показать прогресс"
              aria-label="Показать прогресс"
            >
              <span className="material-symbols-outlined">toolbar</span>
            </button>
            <button 
              className="icon-button dock-button"
              onClick={toggleMenu}
              title={isMenuCollapsed ? 'Развернуть меню' : 'Свернуть меню'}
              aria-label={isMenuCollapsed ? 'Развернуть меню' : 'Свернуть меню'}
            >
              <span className="material-symbols-outlined">
                {isMenuCollapsed ? 'dock_to_left' : 'dock_to_right'}
              </span>
            </button>
          </div>

          <div className="menu-content">
            <div className="menu-scroll">
              {sortedGroups.map((group, groupIndex) => (
                <div 
                  key={group.id} 
                  className="group-section"
                  style={{ marginBottom: groupIndex < sortedGroups.length - 1 ? '17px' : '0' }}
                >
                  <button 
                    className="group-header" 
                    onClick={() => toggleGroup(group.id)}
                    aria-expanded={expandedGroups.has(group.id)}
                  >
                    <span className="group-title">{group.title}</span>
<span
  className={`material-symbols-outlined group-toggle${expandedGroups.has(group.id) ? " expanded" : ""}`}
>
  change_history
</span>


                  </button>
                  
                  {expandedGroups.has(group.id) && (
                    <div className="modules-list">
                      {getModulesForGroup(group.id).map(module => (
                        <button
                          key={module.id}
                          className={`module-item ${selectedModule === module.id ? 'active' : ''}`}
                          onClick={() => handleModuleClick(module.id)}
                        >
                          <span className="module-text">{module.title}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Основной контент */}
        <main className="main-content">
          {/* Прогресс бар */}
          <div className={`progress-bar-container ${isProgressBarVisible ? 'visible' : ''}`}>
            <div className="progress-bar-content">
              <button 
                className="progress-close"
                onClick={() => navigate('/')}
                aria-label="На главную"
              >
                <span className="material-symbols-outlined">door_open</span>
                <span>На Главную</span>
              </button>
              
              <h2 className="course-title">{courseData.title}</h2>
              
              <div className="progress-wrapper">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${courseData.progress}%` }}
                    role="progressbar"
                    aria-valuenow={courseData.progress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  />
                </div>
                <span className="progress-text">{courseData.progress}%</span>
              </div>
            </div>
          </div>

          {/* Контент модуля */}
          <div className="module-content">
            {currentModule && (
              <>
                <h1 className="module-title">{currentModule.title}</h1>
                
                <div className="content-blocks">
                  {moduleContent.map(block => (
                    <article key={block.id} className="content-block">
                      <h3 className="block-title">{block.title}</h3>
                      <div className="block-content">
                        {renderContentBlock(block)}
                      </div>
                    </article>
                  ))}
                </div>

                {moduleContent.length > 0 && (
                  <div className="module-actions">
                    <button 
                      className="complete-module-btn"
                      onClick={handleCompleteModule}
                    >
                      Завершить урок
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default LearningPage;