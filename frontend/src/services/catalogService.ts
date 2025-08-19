// frontend/src/services/catalogService.ts
import { catalogApi } from "../api/axiosInstance";

// === ТИПЫ ===
export interface Course {
  id: number;
  title: string;
  short_description: string;
  full_description?: string;
  image: string | null;
  price: number;
  discount?: number;
  is_free: boolean;
  is_purchased?: boolean;
  modules_count?: number;
  students_count?: number;
  order?: number;
  video?: string | null;
  video_preview?: string | null;
  banner_text?: string | null;
  banner_color_left?: string | null;
  banner_color_right?: string | null;
  group_title?: string | null;
  discount_start?: string | null;
  discount_until?: string | null;
  is_discount_active?: boolean;
}

export interface Module {
  id: number;
  title: string;
  group_title?: string | null;
  order: number;
  sp_award: number;
  blocks_count: number;
  is_completed?: boolean;
}

export interface Banner {
  id: number;
  image: string;
  order: number;
  link?: string | null;
}

export interface PromoCode {
  id: number;
  code: string;
  discount_percent: number;
  valid_until?: string | null;
  max_uses?: number | null;
  uses_left?: number | null;
  is_active: boolean;
}

class CatalogService {
  // CDN URLs
  private readonly PUBLIC_CDN = "https://79340a29-0019-4283-b338-388e7f5c1822.selstorage.ru";
  private readonly PRIVATE_CDN = "https://3e95e171-5a4f-482f-828a-d9394d4fb18e.selcdn.net";

  // Утилиты для форматирования URL
  formatImageUrl(url: string | null): string {
    if (!url) return "";
    if (url.startsWith("http")) return url;
    return `${this.PUBLIC_CDN}/${url}`;
  }

  formatVideoUrl(url: string | null, isPrivate = false): string {
    if (!url) return "";
    if (url.startsWith("http")) return url;
    return isPrivate ? `${this.PRIVATE_CDN}/${url}` : `${this.PUBLIC_CDN}/${url}`;
  }

// === КУРСЫ ===
async getCourses(params?: {
  page?: number;
  limit?: number;
  search?: string;
  is_free?: boolean;
}): Promise<{ courses: Course[]; total: number }> {
  const { data } = await catalogApi.get("/v1/public/courses/", { params });
  const courses = Array.isArray(data) ? data : (data.courses ?? []);
  const total = Array.isArray(data) ? data.length : (data.total ?? courses.length);
  return { courses, total };
}


  async getCourseDetail(courseId: number): Promise<Course> {
    const response = await catalogApi.get(`/v1/public/courses/${courseId}`);
    return response.data;
  }

  async buyCourse(courseId: number, promoCode?: string): Promise<{
    success: boolean;
    message: string;
    purchase_id?: number;
  }> {
      const response = await catalogApi.post(
        `/v1/public/courses/${courseId}/buy/`,
        { course_id: courseId, promo_code: promoCode }
      );
    return response.data;
  }

  async getMyCourses(): Promise<Course[]> {
    const response = await catalogApi.get("/v1/public/my-courses/");
    return response.data.courses || response.data;
  }

  // === БАННЕРЫ ===
  async getBanners(): Promise<Banner[]> {
    const response = await catalogApi.get("/v1/public/banners/");
    return response.data;
  }

  // === ПРОМОКОДЫ ===
  async checkPromoCode(courseId: number, code: string): Promise<{
    valid: boolean;
    discount_percent?: number;
    final_price?: number;
    message?: string;
  }> {
    const response = await catalogApi.post("/v1/public/promocodes/check/", {
      course_id: courseId,
      code: code
    });
    return response.data;
  }

  // === ДАШБОРД ===
  async getDashboardData(): Promise<{
    user_id: number;
    stats: {
      total_courses: number;
      completed_courses: number;
      total_progress_percent: number;
    };
    courses: Array<{
      course_id: number;
      course_title: string;
      image: string | null;
      progress_percent: number;
      is_completed: boolean;
      purchased_at: string;
    }>;
  }> {
    const response = await catalogApi.get("/v1/public/dashboard/");
    return response.data;
  }

  // === ПРОФИЛЬ ===
  async getUserProfile(): Promise<{
    id: number;
    username: string;
    email: string;
  }> {
    const response = await catalogApi.get("/v1/public/profile/");
    return response.data;
  }
}

export default new CatalogService();
