// services/learningService.ts

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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

interface ModuleProgress {
  moduleId: string;
  isCompleted: boolean;
  completedAt?: string;
}

class LearningService {
  private api = axios.create({
    baseURL: `${API_BASE_URL}/learning`,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    // Добавляем интерсептор для токена авторизации
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Получить данные курса
  async getCourseData(courseId: string): Promise<CourseData> {
    try {
      const response = await this.api.get(`/courses/${courseId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching course data:', error);
      throw error;
    }
  }

  // Получить контент модуля
  async getModuleContent(courseId: string, moduleId: string): Promise<ContentBlock[]> {
    try {
      const response = await this.api.get(`/courses/${courseId}/modules/${moduleId}/content`);
      return response.data;
    } catch (error) {
      console.error('Error fetching module content:', error);
      throw error;
    }
  }

  // Отметить модуль как завершенный
  async markModuleCompleted(courseId: string, moduleId: string): Promise<void> {
    try {
      await this.api.post(`/courses/${courseId}/modules/${moduleId}/complete`);
    } catch (error) {
      console.error('Error marking module as completed:', error);
      throw error;
    }
  }

  // Получить прогресс пользователя по курсу
  async getUserProgress(courseId: string): Promise<ModuleProgress[]> {
    try {
      const response = await this.api.get(`/courses/${courseId}/progress`);
      return response.data;
    } catch (error) {
      console.error('Error fetching user progress:', error);
      throw error;
    }
  }

  // Обновить позицию пользователя в курсе (для сохранения места где остановился)
  async updateUserPosition(courseId: string, moduleId: string, position: number): Promise<void> {
    try {
      await this.api.put(`/courses/${courseId}/position`, {
        moduleId,
        position,
      });
    } catch (error) {
      console.error('Error updating user position:', error);
      throw error;
    }
  }

  // Получить список всех курсов пользователя
  async getUserCourses(): Promise<CourseData[]> {
    try {
      const response = await this.api.get('/user/courses');
      return response.data;
    } catch (error) {
      console.error('Error fetching user courses:', error);
      throw error;
    }
  }

  // Проверить доступ к курсу
  async checkCourseAccess(courseId: string): Promise<boolean> {
    try {
      const response = await this.api.get(`/courses/${courseId}/access`);
      return response.data.hasAccess;
    } catch (error) {
      console.error('Error checking course access:', error);
      return false;
    }
  }
}

export const learningService = new LearningService();