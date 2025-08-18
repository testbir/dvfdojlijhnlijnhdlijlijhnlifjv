// frontend/src/services/dashboardService.ts

import { catalogApi } from "../api/catalogApi";

export interface UserStats {
  total_courses: number;
  completed_courses: number;
  total_progress_percent: number;
}

export interface UserCourse {
  course_id: number;
  course_title: string;
  image: string | null;
  progress_percent: number;
  is_completed: boolean;
  purchased_at: string;
}

export interface DashboardData {
  user_id: number;
  stats: UserStats;
  courses: UserCourse[];
  recent_progress: Array<{
    course_id: number;
    course_title: string;
    total_modules: number;
    completed_modules: number;
    progress_percent: number;
  }>;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
}

class DashboardService {
  // Получение профиля пользователя (из catalog, который проксирует к auth)
  async getUserProfile(): Promise<UserProfile> {
    const response = await catalogApi.get("/v1/public/profile");
    return response.data;
  }

  // Получение данных дашборда
  async getDashboardData(): Promise<DashboardData> {
    const response = await catalogApi.get("/v1/public/dashboard");
    return response.data;
  }

  // Получение статистики
  async getUserStats(): Promise<UserStats> {
    const response = await catalogApi.get("/v1/public/stats");
    return response.data;
  }

  // Комбинированный запрос
  async getFullDashboard(): Promise<{
    profile: UserProfile;
    dashboard: DashboardData;
  }> {
    const [profile, dashboard] = await Promise.all([
      this.getUserProfile(),
      this.getDashboardData()
    ]);

    return { profile, dashboard };
  }
}

export default new DashboardService();
