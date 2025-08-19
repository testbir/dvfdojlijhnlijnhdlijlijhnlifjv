// frontend/src/pages/LearningPage.tsx

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DOMPurify from 'dompurify';
import learningService from '../services/learningService';
import catalogService from '../services/catalogService';
import '../styles/LearningPage.scss';

import Prism from 'prismjs';
import 'prismjs/plugins/line-numbers/prism-line-numbers.css';
import 'prismjs/plugins/line-numbers/prism-line-numbers';
import 'prism-themes/themes/prism-vsc-dark-plus.css';

import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-markup';
import 'prismjs/components/prism-css';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-rust';
import 'prismjs/components/prism-php';
import 'prismjs/components/prism-ruby';
import 'prismjs/components/prism-markdown';
import 'prismjs/components/prism-docker';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-scss';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-csharp';
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cpp';

interface UIModule {
  id: number;
  title: string;
  groupId: string;
  order: number;
}
interface UIGroup {
  id: string;
  title: string;
  order: number;
}
interface UIContentBlock {
  id: string;
  type: 'text' | 'code' | 'video' | 'image';
  title: string;
  content: string;
  order: number;
  language?: string;
}
interface CourseData {
  id: number;
  title: string;
  groups: UIGroup[];
  modules: UIModule[];
  progress: number;
}

const LANGUAGE_MAP: Record<string, string> = {
  html: 'markup',
  dockerfile: 'docker',
  plaintext: 'plain',
  text: 'plain',
  shell: 'bash',
  sh: 'bash',
  powershell: 'bash',
  cmd: 'bash',
};

const LearningPage: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();

  const [courseData, setCourseData] = useState<CourseData | null>(null);
  const [selectedModule, setSelectedModule] = useState<number | null>(null);
  const [moduleContent, setModuleContent] = useState<UIContentBlock[]>([]);
  const [isMenuCollapsed, setIsMenuCollapsed] = useState(false);
  const [isProgressBarVisible, setIsProgressBarVisible] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedCodeId, setCopiedCodeId] = useState<string | null>(null);

  useEffect(() => {
    if (!courseId) return;
    loadCourseData();
  }, [courseId]);

  useEffect(() => {
    if (!selectedModule || !courseId) return;
    loadModuleContent(selectedModule);
  }, [selectedModule, courseId]);

  useEffect(() => {
    setTimeout(() => Prism.highlightAll(), 0);
  }, [moduleContent]);

  const loadCourseData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const info = await learningService.getLearningCourseInfo(Number(courseId));

      const uiModules: UIModule[] = info.modules
        .slice()
        .sort((a, b) => a.order - b.order)
        .map((m) => ({
          id: m.id,
          title: m.title,
          groupId: m.group_title || 'Курс',
          order: m.order,
        }));

      const titles = Array.from(new Set(uiModules.map((m) => m.groupId)));
      const uiGroups: UIGroup[] = titles.map((t, i) => ({ id: t, title: t, order: i }));

      setCourseData({
        id: info.course.id,
        title: info.course.title,
        groups: uiGroups,
        modules: uiModules,
        progress: Math.round(info.progress.progress_percent),
      });

      setExpandedGroups(new Set(uiGroups.map((g) => g.id)));
      if (uiModules.length) setSelectedModule(uiModules[0].id);
    } catch (e: any) {
      if (e?.response?.status === 403) setError('У вас нет доступа к этому курсу');
      else setError('Не удалось загрузить данные курса');
      console.error('Error loading course data:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const loadModuleContent = async (moduleId: number) => {
    try {
      const blocks = await learningService.getModuleBlocks(moduleId);
      const sorted = (blocks || [])
        .slice()
        .sort((a, b) => a.order - b.order)
        .map<UIContentBlock>((b) => ({
          id: String(b.id),
          type: (['text', 'code', 'video', 'image'] as const).includes(b.type as any)
            ? (b.type as any)
            : 'text',
          title: b.title,
          content:
            b.type === 'video'
              ? catalogService.formatVideoUrl(b.video_url || b.content)
              : b.type === 'image'
              ? catalogService.formatImageUrl(b.image_url || b.content)
              : b.content,
          order: b.order,
          language: b.language,
        }));
      setModuleContent(sorted);
    } catch (e) {
      console.error('Error loading module content:', e);
    }
  };

  const toggleGroup = useCallback((groupId: string) => {
    setExpandedGroups((prev) => {
      const next = new Set(prev);
      next.has(groupId) ? next.delete(groupId) : next.add(groupId);
      return next;
    });
  }, []);

  const handleModuleClick = useCallback((moduleId: number) => {
    setSelectedModule(moduleId);
  }, []);

  const toggleMenu = useCallback(() => setIsMenuCollapsed((p) => !p), []);
  const toggleProgressBar = useCallback(() => setIsProgressBarVisible((p) => !p), []);

  const handleCopyCode = useCallback((blockId: string, code: string) => {
    navigator.clipboard.writeText(code).then(() => {
      setCopiedCodeId(blockId);
      setTimeout(() => setCopiedCodeId(null), 2000);
    });
  }, []);

  const handleCompleteModule = useCallback(async () => {
    if (!selectedModule || !courseId || !courseData) return;
    try {
      await learningService.completeModule(selectedModule);

      const sorted = courseData.modules.slice().sort((a, b) => a.order - b.order);
      const idx = sorted.findIndex((m) => m.id === selectedModule);
      const next = sorted[idx + 1]?.id ?? null;
      if (next) setSelectedModule(next);

      const progress = await learningService.getCourseProgress(Number(courseId));
      setCourseData((prev) => (prev ? { ...prev, progress: Math.round(progress.progress_percent) } : prev));
    } catch (e) {
      console.error('Error completing module:', e);
    }
  }, [selectedModule, courseId, courseData]);

  const renderContentBlock = useCallback(
    (block: UIContentBlock) => {
      switch (block.type) {
        case 'text':
          return (
            <div
              className="content-text"
              dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(block.content) }}
            />
          );

        case 'code': {
          const language = (block.language || 'plaintext').toLowerCase().trim();
          const prismLanguage = LANGUAGE_MAP[language] || language;
          return (
            <div className="content-code-wrapper">
              <pre className="content-code line-numbers">
                <code className={`language-${prismLanguage}`}>{block.content}</code>
              </pre>
              <button
                className={`copy-button ${copiedCodeId === block.id ? 'copied' : ''}`}
                onClick={() => handleCopyCode(block.id, block.content)}
                title="Копировать код"
              >
                <span className="material-symbols-outlined">
                  {copiedCodeId === block.id ? 'check' : 'content_copy'}
                </span>
                <span className="copy-text">{copiedCodeId === block.id ? 'Copied!' : 'Copy Code'}</span>
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
    },
    [copiedCodeId, handleCopyCode]
  );

  const sortedGroups = useMemo(
    () => (courseData?.groups.slice().sort((a, b) => a.order - b.order) || []),
    [courseData?.groups]
  );

  const getModulesForGroup = useCallback(
    (groupId: string) =>
      courseData?.modules
        .filter((m) => m.groupId === groupId)
        .slice()
        .sort((a, b) => a.order - b.order) || [],
    [courseData?.modules]
  );

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

  if (!courseData) return null;

  const currentModule = selectedModule
    ? courseData.modules.find((m) => m.id === selectedModule)
    : null;

  return (
    <div className="learning-page">
      <div className="glass-container">
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
              {sortedGroups.map((group, i) => (
                <div key={group.id} className="group-section" style={{ marginBottom: i < sortedGroups.length - 1 ? '17px' : '0' }}>
                  <button
                    className="group-header"
                    onClick={() => toggleGroup(group.id)}
                    aria-expanded={expandedGroups.has(group.id)}
                  >
                    <span className="group-title">{group.title}</span>
                    <span className={`material-symbols-outlined group-toggle${expandedGroups.has(group.id) ? ' expanded' : ''}`}>
                      change_history
                    </span>
                  </button>

                  {expandedGroups.has(group.id) && (
                    <div className="modules-list">
                      {getModulesForGroup(group.id).map((module) => (
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

        <main className="main-content">
          <div className={`progress-bar-container ${isProgressBarVisible ? 'visible' : ''}`}>
            <div className="progress-bar-content">
              <button className="progress-close" onClick={() => navigate('/')} aria-label="На главную">
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

          <div className="module-content">
            {currentModule && (
              <>
                <h1 className="module-title">{currentModule.title}</h1>

                <div className="content-blocks">
                  {moduleContent.map((block) => (
                    <article key={block.id} className="content-block">
                      <h3 className="block-title">{block.title}</h3>
                      <div className="block-content">{renderContentBlock(block)}</div>
                    </article>
                  ))}
                </div>

                {moduleContent.length > 0 && (
                  <div className="module-actions">
                    <button className="complete-module-btn" onClick={handleCompleteModule}>
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
