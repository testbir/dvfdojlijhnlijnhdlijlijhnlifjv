// frontend/src/services/learningService.ts
import { learningApi } from "../api/axiosInstance";

export interface ContentBlock {
  id: number;
  type: 'text' | 'code' | 'video' | 'image' | 'quiz' | 'exercise';
  title: string;
  content: string;
  order: number;
  language?: string;
  video_url?: string;
  image_url?: string;
}

export interface ModuleProgress {
  module_id: number;
  is_completed: boolean;
  completed_at?: string;
}

export interface CourseProgress {
  course_id: number;
  total_modules: number;
  completed_modules: number;
  progress_percent: number;
  module_progress: ModuleProgress[];
}

class LearningService {
  async getCourseModules(courseId: number): Promise<{
    modules: Array<{
      id: number;
      title: string;
      group_title?: string;
      order: number;
      sp_award: number;
      blocks: ContentBlock[];
    }>;
  }> {
    const response = await learningApi.get(`/v1/public/courses/${courseId}/modules/`);
    return response.data;
  }

  async getModuleBlocks(moduleId: number): Promise<ContentBlock[]> {
    const response = await learningApi.get(`/v1/public/modules/${moduleId}/blocks/`);
    return response.data.blocks || response.data;
  }

  async getCourseProgress(courseId: number): Promise<CourseProgress> {
    const response = await learningApi.get(`/v1/public/courses/${courseId}/progress/`);
    return response.data;
  }

  async completeModule(moduleId: number): Promise<{
    success: boolean;
    sp_awarded: number;
    new_balance: number;
    message: string;
  }> {
    const response = await learningApi.post(`/v1/public/modules/${moduleId}/complete/`);
    return response.data;
  }

  async getLearningCourseInfo(courseId: number): Promise<{
    course: {
      id: number;
      title: string;
      modules_count: number;
    };
    modules: Array<{
      id: number;
      title: string;
      group_title?: string;
      order: number;
      sp_award: number;
      is_completed: boolean;
    }>;
    progress: CourseProgress;
  }> {
    const [modulesData, progressData] = await Promise.all([
      this.getCourseModules(courseId),
      this.getCourseProgress(courseId)
    ]);

    const modulesWithProgress = modulesData.modules.map(module => ({
      ...module,
      is_completed: progressData.module_progress.some(
        p => p.module_id === module.id && p.is_completed
      )
    }));

    return {
      course: {
        id: courseId,
        title: "Course",
        modules_count: modulesData.modules.length
      },
      modules: modulesWithProgress,
      progress: progressData
    };
  }
}

export default new LearningService();
