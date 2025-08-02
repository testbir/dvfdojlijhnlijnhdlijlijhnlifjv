// src/services/catalogService.ts

import catalogApi from "../api/catalogApi";

// === ТИПЫ ===

export interface Course {
  id: number;
  title: string;
  short_description: string;
  image: string;
  price: number;
  final_price: number;
  is_free: boolean;
  has_access: boolean;
  button_text: string;
  order?: number;
  discount?: number;
  is_discount_active?: boolean;
  discount_ends_in?: number;
}

export interface CourseDetail {
  id: number;
  title: string;
  full_description: string;
  short_description: string;
  image: string;
  is_free: boolean;
  price: number;
  discount: number;
  final_price: number;
  has_access: boolean;
  button_text: string;
  video?: string;
  video_preview?: string;
  banner_text?: string;
  banner_color_left?: string;
  banner_color_right?: string;
  group_title?: string;
  discount_start?: string;
  discount_until?: string;
  discount_ends_in?: number;
  is_discount_active?: boolean;
}

export interface Banner {
  id: number;
  image: string;
  order: number;
  link?: string;
}

export interface CourseModule {
  id: number;
  title: string;
  group_title?: string;
  order: number;
}

export interface CourseStructure {
  course_id: number;
  modules: CourseModule[];
}

export interface BuyCourseRequest {
  payment_id?: string;
}

export interface BuyCourseResponse {
  success: boolean;
  message: string;
}

export interface CourseAccessResponse {
  has_access: boolean;
  requires_auth: boolean;
  course_type?: string;
  message?: string;
}

// === СЕРВИС ===

class CatalogService {
  // Утилита для форматирования URL изображений
  formatImageUrl(url: string): string {
    if (!url) return "";
    if (url.startsWith("http")) return url;
    return `https://course-content.s3.ru-7.storage.selcloud.ru/${url}`;
  }

  // === КУРСЫ ===

  // Получение списка всех курсов
  async getCourses(): Promise<Course[]> {
    const response = await catalogApi.get("/courses/");
    if (!Array.isArray(response.data)) {
      throw new Error("Ожидался массив курсов");
    }
    
    return response.data.sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
  }

  // Получение детальной информации о курсе
  async getCourseDetail(courseId: number): Promise<CourseDetail> {
    const response = await catalogApi.get(`/courses/${courseId}/`);
    return response.data;
  }

  // Получение структуры курса (модули)
  async getCourseStructure(courseId: number): Promise<CourseStructure> {
    const response = await catalogApi.get(`/courses/${courseId}/structure/`);
    return response.data;
  }

  // Проверка доступа к курсу
  async checkCourseAccess(courseId: number): Promise<CourseAccessResponse> {
    const response = await catalogApi.post(`/courses/${courseId}/check-access/`);
    return response.data;
  }

  // Покупка курса
  async buyCourse(courseId: number, data: BuyCourseRequest = {}): Promise<BuyCourseResponse> {
    const response = await catalogApi.post(`/courses/${courseId}/buy/`, data);
    return response.data;
  }

  // === БАННЕРЫ ===

  // Получение баннеров для главной страницы
  async getBanners(limit = 2): Promise<Banner[]> {
    const response = await catalogApi.get("/internal/banners/");
    if (!Array.isArray(response.data)) {
      throw new Error("Ожидался массив баннеров");
    }

    return response.data
      .sort((a, b) => a.order - b.order)
      .slice(0, limit);
  }

  // === ПОИСК И ФИЛЬТРАЦИЯ ===

  // Фильтрация курсов по поисковому запросу
  filterCourses(courses: Course[], searchQuery: string): Course[] {
    if (!searchQuery.trim()) return courses;
    
    const query = searchQuery.toLowerCase();
    return courses.filter((course) =>
      course.title.toLowerCase().includes(query) ||
      course.short_description.toLowerCase().includes(query)
    );
  }

  // Получение курсов с поиском
  async getCoursesWithSearch(searchQuery?: string): Promise<Course[]> {
    const courses = await this.getCourses();
    return searchQuery ? this.filterCourses(courses, searchQuery) : courses;
  }

  // === ПРОМОКОДЫ ===

  // Проверка промокода
  async checkPromocode(code: string, courseId?: number) {
    const params = courseId ? { course_id: courseId } : {};
    const response = await catalogApi.post("/promocodes/check/", { code, ...params });
    return response.data;
  }

  // Применение промокода
  async usePromocode(code: string, courseId?: number) {
    const params = courseId ? { course_id: courseId } : {};
    const response = await catalogApi.post("/promocodes/use/", { code, ...params });
    return response.data;
  }

  // === КЭШИРОВАНИЕ ===

  private cache: {
    courses: Course[] | null;
    banners: Banner[] | null;
    coursesTimestamp: number;
    bannersTimestamp: number;
  } = {
    courses: null,
    banners: null,
    coursesTimestamp: 0,
    bannersTimestamp: 0,
  };

  private readonly CACHE_TIME = 5 * 60 * 1000; // 5 минут

  // Получение курсов с кэшированием
  async getCachedCourses(forceRefresh = false): Promise<Course[]> {
    const now = Date.now();
    
    if (
      !forceRefresh &&
      this.cache.courses &&
      (now - this.cache.coursesTimestamp) < this.CACHE_TIME
    ) {
      return this.cache.courses;
    }

    const courses = await this.getCourses();
    this.cache.courses = courses;
    this.cache.coursesTimestamp = now;
    
    return courses;
  }

  // Получение баннеров с кэшированием
  async getCachedBanners(limit = 2, forceRefresh = false): Promise<Banner[]> {
    const now = Date.now();
    
    if (
      !forceRefresh &&
      this.cache.banners &&
      (now - this.cache.bannersTimestamp) < this.CACHE_TIME
    ) {
      return this.cache.banners.slice(0, limit);
    }

    const banners = await this.getBanners(limit);
    this.cache.banners = banners;
    this.cache.bannersTimestamp = now;
    
    return banners;
  }

  // Очистка кэша
  clearCache() {
    this.cache = {
      courses: null,
      banners: null,
      coursesTimestamp: 0,
      bannersTimestamp: 0,
    };
  }

  // === КОМБИНИРОВАННЫЕ МЕТОДЫ ===

  // Получение всех данных для главной страницы
  async getHomePageData(searchQuery?: string): Promise<{
    courses: Course[];
    banners: Banner[];
  }> {
    const [courses, banners] = await Promise.all([
      this.getCoursesWithSearch(searchQuery),
      this.getCachedBanners(2)
    ]);

    return { courses, banners };
  }

  // Получение полных данных о курсе (детали + структура)
  async getFullCourseData(courseId: number): Promise<{
    course: CourseDetail;
    structure: CourseStructure;
    access: CourseAccessResponse;
  }> {
    const [course, structure, access] = await Promise.all([
      this.getCourseDetail(courseId),
      this.getCourseStructure(courseId),
      this.checkCourseAccess(courseId)
    ]);

    return { course, structure, access };
  }
}

export default new CatalogService();