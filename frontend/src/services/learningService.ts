// frontend/src/services/learningService.ts

import learningApi from "../api/learningApi"; 

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
  language?: string; // Добавляем поддержку языка
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
  private api = learningApi;

  // Получить данные курса
  async getCourseData(courseId: string): Promise<CourseData> {
    const { data } = await this.api.get<CourseData>(
      `/learning/courses/${courseId}`
    );
    return data;
  }

  // Получить контент модуля (теперь включает language для блоков кода)
  async getModuleContent(
    courseId: string,
    moduleId: string
  ): Promise<ContentBlock[]> {
    const { data } = await this.api.get<ContentBlock[]>(
      `/learning/courses/${courseId}/modules/${moduleId}/content`
    );
    return data;
  }
  
  // Отметить модуль как завершенный
  async markModuleCompleted(courseId: string, moduleId: string): Promise<void> {
    try {
      await this.api.post(`/learning/courses/${courseId}/modules/${moduleId}/complete`);
    } catch (error) {
      console.error('Error marking module as completed:', error);
      throw error;
    }
  }

  // Получить прогресс пользователя по курсу
  async getUserProgress(courseId: string): Promise<ModuleProgress[]> {
    try {
      const response = await this.api.get(`/learning/courses/${courseId}/progress`);
      return response.data;
    } catch (error) {
      console.error('Error fetching user progress:', error);
      throw error;
    }
  }

  // Обновить позицию пользователя в курсе
  async updateUserPosition(courseId: string, moduleId: string, position: number): Promise<void> {
    try {
      await this.api.put(`/learning/courses/${courseId}/position`, {
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
      const response = await this.api.get(`/learning/courses/${courseId}/access`);
      return response.data.hasAccess;
    } catch (error) {
      console.error('Error checking course access:', error);
      return false;
    }
  }
}

export const learningService = new LearningService();