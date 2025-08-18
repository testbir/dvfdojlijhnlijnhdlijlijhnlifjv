// frontend/src/services/learningService.ts

import { learningApi } from "../api/learningApi";

export interface ContentBlock {
  id: number;
  type: 'text' | 'code' | 'video' | 'image';
  title: string;
  content: string;
  order: number;
  language?: string;
}

export interface ModuleWithBlocks {
  id: number;
  title: string;
  blocks: ContentBlock[];
}

export interface CourseProgress {
  course_id: number;
  total_modules: number;
  completed_modules: number;
  progress_percent: number;
  completed_module_ids: number[];
}

class LearningService {
  // Получение модулей курса с прогрессом
  async getCourseModules(courseId: number): Promise<{
    modules: ModuleWithBlocks[];
    progress: CourseProgress;
  }> {
    const response = await catalogApi.get(`/v1/public/courses/${courseId}/modules`);
    return response.data;
  }

  // Получение блоков модуля
  async getModuleBlocks(moduleId: number): Promise<ContentBlock[]> {
    const response = await learningApi.get(`/v1/public/modules/${moduleId}/blocks`);
    return response.data;
  }

  // Отметить модуль как завершенный
  async completeModule(moduleId: number): Promise<{
    success: boolean;
    sp_awarded: number;
    new_balance: number;
  }> {
    const response = await learningApi.post(`/v1/public/progress/module/${moduleId}/complete`);
    return response.data;
  }

  // Получение прогресса по курсу
  async getCourseProgress(courseId: number): Promise<CourseProgress> {
    const response = await learningApi.get(`/v1/public/progress/course/${courseId}`);
    return response.data;
  }
}

export default new LearningService();
