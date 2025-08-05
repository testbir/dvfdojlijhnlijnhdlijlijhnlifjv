// frontend/src/pages/LearningPage.tsx

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { learningService } from '../services/learningService';
import './LearningPage.css';

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
  isExpanded?: boolean;
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

  useEffect(() => {
    loadCourseData();
  }, [courseId]);

  useEffect(() => {
    if (selectedModule) {
      loadModuleContent(selectedModule);
    }
  }, [selectedModule]);

  const loadCourseData = async () => {
    try {
      const data = await learningService.getCourseData(courseId!);
      setCourseData(data);
      // Раскрываем все группы по умолчанию
      setExpandedGroups(new Set(data.groups.map(g => g.id)));
      // Выбираем первый модуль
      if (data.modules.length > 0) {
        setSelectedModule(data.modules[0].id);
      }
    } catch (error) {
      console.error('Error loading course data:', error);
    }
  };

  const loadModuleContent = async (moduleId: string) => {
    try {
      const content = await learningService.getModuleContent(courseId!, moduleId);
      setModuleContent(content);
    } catch (error) {
      console.error('Error loading module content:', error);
    }
  };

  const toggleGroup = (groupId: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupId)) {
      newExpanded.delete(groupId);
    } else {
      newExpanded.add(groupId);
    }
    setExpandedGroups(newExpanded);
  };

  const handleModuleClick = (moduleId: string) => {
    setSelectedModule(moduleId);
  };

  const toggleMenu = () => {
    setIsMenuCollapsed(!isMenuCollapsed);
  };

  const toggleProgressBar = () => {
    setIsProgressBarVisible(!isProgressBarVisible);
  };

  const renderContentBlock = (block: ContentBlock) => {
    switch (block.type) {
      case 'text':
        return <div className="content-text" dangerouslySetInnerHTML={{ __html: block.content }} />;
      case 'code':
        return <pre className="content-code"><code>{block.content}</code></pre>;
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
  };

  if (!courseData) {
    return <div className="loading">Загрузка...</div>;
  }

  const currentModule = courseData.modules.find(m => m.id === selectedModule);

  return (
    <div className="learning-page">
      <div className="glass-container">
        {/* Левое меню */}
        <div className={`left-menu ${isMenuCollapsed ? 'collapsed' : ''}`}>
          <div className="menu-controls">
            <span 
              className="material-symbols-outlined icon-button"
              onClick={toggleProgressBar}
              title="Показать прогресс"
            >
              toolbar
            </span>
            <span 
              className="material-symbols-outlined icon-button"
              onClick={toggleMenu}
              title={isMenuCollapsed ? 'Развернуть меню' : 'Свернуть меню'}
            >
              {isMenuCollapsed ? 'dock_to_left' : 'dock_to_right'}
            </span>
          </div>

          {!isMenuCollapsed && (
            <div className="menu-content">
              {courseData.groups.map(group => (
                <div key={group.id} className="group-section">
                  <div className="group-header" onClick={() => toggleGroup(group.id)}>
                    <span className={`group-toggle ${expandedGroups.has(group.id) ? 'expanded' : ''}`}>
                      ▶
                    </span>
                    <span className="group-title">{group.title}</span>
                  </div>
                  {expandedGroups.has(group.id) && (
                    <div className="modules-list">
                      {courseData.modules
                        .filter(module => module.groupId === group.id)
                        .sort((a, b) => a.order - b.order)
                        .map(module => (
                          <div
                            key={module.id}
                            className={`module-item ${selectedModule === module.id ? 'active' : ''}`}
                            onClick={() => handleModuleClick(module.id)}
                          >
                            {module.title}
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Основной контент */}
        <div className="main-content">
          {/* Прогресс бар */}
          {isProgressBarVisible && (
            <div className="progress-bar-container">
              <div className="progress-bar-header">
                <span 
                  className="material-symbols-outlined icon-button"
                  onClick={toggleProgressBar}
                  title="Закрыть"
                >
                  door_open
                </span>
                <button 
                  className="home-button"
                  onClick={() => navigate('/')}
                >
                  На главную
                </button>
              </div>
              <h2 className="course-title">{courseData.title}</h2>
              <div className="progress-wrapper">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${courseData.progress}%` }}
                  />
                </div>
                <span className="progress-text">{courseData.progress}%</span>
              </div>
            </div>
          )}

          {/* Контент модуля */}
          <div className="module-content">
            {currentModule && (
              <>
                <h1 className="module-title">{currentModule.title}</h1>
                <div className="content-blocks">
                  {moduleContent.map(block => (
                    <div key={block.id} className="content-block">
                      <h3 className="block-title">{block.title}</h3>
                      <div className="block-content">
                        {renderContentBlock(block)}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningPage;