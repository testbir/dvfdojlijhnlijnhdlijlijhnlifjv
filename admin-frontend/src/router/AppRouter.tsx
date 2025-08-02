// router/AppRouter.tsx

import { Routes, Route } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import CoursesPage from '../pages/CoursesPage';
import CourseCreatePage from '../pages/CourseCreatePage';
import CourseStructurePage from '../pages/CourseStructurePage';
import CourseEditPage from '../pages/CourseEditPage';
import ModuleCreatePage from '../pages/ModuleCreatePage';
import ModuleEditPage from '../pages/ModuleEditPage';
import ModuleBlocksPage from '../pages/ModuleBlocksPage';
import ProtectedRoute from '../components/ProtectedRoute';
import BlockCreatePage from '../pages/BlockCreatePage';
import BlockEditPage from '../pages/BlockEditPage';
import BannerCreatePage from '../pages/BannerCreatePage';
import BannerEditPage from '../pages/BannerEditPage';

// Новые импорты
import UsersPage from '../pages/UsersPage';
import StatisticsPage from '../pages/StatisticsPage';
import PromoCodesPage from '../pages/PromoCodesPage';
import CourseModalPage from '../pages/CourseModalPage';
import StudentWorksPage from '../pages/StudentWorksPage';

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Главная страница - список курсов */}
      <Route path="/" element={
        <ProtectedRoute>
          <CoursesPage />
        </ProtectedRoute>
      } />

      {/* Управление курсами */}
      <Route path="/courses/create" element={
        <ProtectedRoute>
          <CourseCreatePage />
        </ProtectedRoute>
      } />

      <Route path="/courses/:courseId/structure" element={
        <ProtectedRoute>
          <CourseStructurePage />
        </ProtectedRoute>
      } />

      <Route path="/courses/:courseId/edit" element={
        <ProtectedRoute>
          <CourseEditPage />
        </ProtectedRoute>
      } />

      {/* НОВЫЕ МАРШРУТЫ ДЛЯ ДОПОЛНИТЕЛЬНЫХ ЭЛЕМЕНТОВ */}
      <Route path="/courses/:courseId/modal" element={
        <ProtectedRoute>
          <CourseModalPage />
        </ProtectedRoute>
      } />

      <Route path="/courses/:courseId/student-works" element={
        <ProtectedRoute>
          <StudentWorksPage />
        </ProtectedRoute>
      } />

      <Route path="/courses/:courseId/modules/create" element={
        <ProtectedRoute>
          <ModuleCreatePage />
        </ProtectedRoute>
      } />

      <Route path="/modules/:moduleId/edit" element={
        <ProtectedRoute>
          <ModuleEditPage />
        </ProtectedRoute>
      } />

      <Route path="/modules/:moduleId/blocks" element={
        <ProtectedRoute>
          <ModuleBlocksPage />
        </ProtectedRoute>
      } />

      <Route path="/modules/:moduleId/blocks/create" element={
        <ProtectedRoute>
          <BlockCreatePage />
        </ProtectedRoute>
      } />

      <Route path="/blocks/:blockId/edit" element={
        <ProtectedRoute>
          <BlockEditPage />
        </ProtectedRoute>
      } />

      {/* Управление баннерами */}
      <Route path="/banners/create" element={
        <ProtectedRoute>
          <BannerCreatePage />
        </ProtectedRoute>
      } />

      <Route path="/banners/:id" element={
        <ProtectedRoute>
          <BannerEditPage />
        </ProtectedRoute>
      } />

      {/* Управление пользователями */}
      <Route path="/users" element={
        <ProtectedRoute>
          <UsersPage />
        </ProtectedRoute>
      } />

      {/* Статистика и аналитика */}
      <Route path="/statistics" element={
        <ProtectedRoute>
          <StatisticsPage />
        </ProtectedRoute>
      } />

      {/* Промокоды */}
      <Route path="/promo-codes" element={
        <ProtectedRoute>
          <PromoCodesPage />
        </ProtectedRoute>
      } />

      {/* Email рассылки */}
      <Route path="/email-campaigns" element={
        <ProtectedRoute>
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <h1>Email рассылки</h1>
            <p>Функционал в разработке</p>
          </div>
        </ProtectedRoute>
      } />

      {/* Резервные копии */}
      <Route path="/backups" element={
        <ProtectedRoute>
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <h1>Резервные копии</h1>
            <p>Функционал в разработке</p>
          </div>
        </ProtectedRoute>
      } />

      {/* Настройки системы */}
      <Route path="/settings" element={
        <ProtectedRoute>
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <h1>Настройки</h1>
            <p>Функционал в разработке</p>
          </div>
        </ProtectedRoute>
      } />

      {/* 404 - Страница не найдена */}
      <Route path="*" element={
        <ProtectedRoute>
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <h1>404 - Страница не найдена</h1>
            <p>Запрашиваемая страница не существует</p>
          </div>
        </ProtectedRoute>
      } />
    </Routes>
  );
}