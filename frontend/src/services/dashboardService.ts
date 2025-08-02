// src/services/dashboardService.ts

// src/services/dashboardService.ts

import catalogApi from "../api/catalogApi";
// Убираем authApi, используем только catalogApi

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

export interface UserData {
  id: number;
  username: string;
  email: string;
}

class DashboardService {
  // Получение данных пользователя из catalog_service (который запрашивает auth_service)
  async getUserData(): Promise<UserData> {
    try {
      console.log('📡 Запрос данных пользователя к catalog API...');
      const response = await catalogApi.get('/api/profile/');
      console.log('📋 Ответ API пользователя:', response);
      console.log('📋 Данные пользователя:', response.data);
      
      // Проверяем структуру ответа
      if (!response.data) {
        throw new Error('Пустой ответ от API');
      }
      
      if (!response.data.username) {
        console.warn('⚠️ В ответе отсутствует username:', response.data);
      }
      
      return response.data;
    } catch (error) {
      console.error('❌ Ошибка получения данных пользователя:', error);
      throw error;
    }
  }

  // Получение dashboard данных из catalog_service
  async getDashboardData(): Promise<DashboardData> {
    try {
      console.log('📡 Запрос данных dashboard к API...');
      const response = await catalogApi.get('/api/dashboard/');
      console.log('📋 Ответ API dashboard:', response);
      return response.data;
    } catch (error) {
      console.error('❌ Ошибка получения данных dashboard:', error);
      throw error;
    }
  }

  // Получение только статистики (быстрый запрос)
  async getUserStats(): Promise<UserStats> {
    const response = await catalogApi.get('/api/stats/');
    return response.data;
  }

  // Получение списка всех курсов пользователя
  async getMyCourses() {
    const response = await catalogApi.get('/api/my-courses/');
    return response.data;
  }

  // Комбинированный запрос - все данные сразу
  async getFullDashboard(): Promise<{
    userData: UserData;
    dashboardData: DashboardData;
  }> {
    try {
      console.log('📡 Запрос полных данных dashboard...');
      
      // Теперь оба запроса идут к catalog_service
      const [userResponse, dashboardResponse] = await Promise.all([
        this.getUserData(),
        this.getDashboardData()
      ]);

      console.log('✅ Все данные загружены успешно');
      return {
        userData: userResponse,
        dashboardData: dashboardResponse
      };
    } catch (error) {
      console.error('❌ Ошибка получения полных данных dashboard:', error);
      throw error;
    }
  }

  // Кэширование данных (опционально)
  private cachedData: {
    userData: UserData | null;
    dashboardData: DashboardData | null;
    timestamp: number;
  } = {
    userData: null,
    dashboardData: null,
    timestamp: 0
  };

  // Получение данных с кэшированием (5 минут)
  async getCachedDashboard(forceRefresh = false): Promise<{
    userData: UserData;
    dashboardData: DashboardData;
  }> {
    const CACHE_TIME = 5 * 60 * 1000; // 5 минут
    const now = Date.now();
    
    if (
      !forceRefresh &&
      this.cachedData.userData &&
      this.cachedData.dashboardData &&
      (now - this.cachedData.timestamp) < CACHE_TIME
    ) {
      console.log('📦 Используем кэшированные данные');
      return {
        userData: this.cachedData.userData,
        dashboardData: this.cachedData.dashboardData
      };
    }

    const data = await this.getFullDashboard();
    
    this.cachedData = {
      userData: data.userData,
      dashboardData: data.dashboardData,
      timestamp: now
    };

    return data;
  }

  // Очистка кэша
  clearCache() {
    this.cachedData = {
      userData: null,
      dashboardData: null,
      timestamp: 0
    };
  }
}

export default new DashboardService();