// frontend/src/services/courseService.ts
import { catalogApi } from "../api/catalogApi";

export interface Course {
  id: number;
  title: string;
  short_description: string;
  full_description: string;
  image: string | null;
  is_free: boolean;
  price: number;
  discount: number | null;
  is_purchased?: boolean;
  modules_count?: number;
  students_count?: number;
}

export interface CourseDetail extends Course {
  video: string | null;
  video_preview: string | null;
  modules: Module[];
  is_purchased: boolean;
  purchase_date?: string;
}

export interface Module {
  id: number;
  title: string;
  group_title?: string;
  order: number;
  sp_award: number;
  blocks_count: number;
}

class CourseService {
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

  async getCourse(courseId: number): Promise< CourseDetail > {
    const response = await catalogApi.get(`/v1/public/courses/${courseId}`);
    return response.data;
  }

  async buyCourse(courseId: number, promoCode?: string): Promise<{
    success: boolean;
    message: string;
    purchase_id?: number;
  }> {
    const response = await catalogApi.post("/v1/public/buy-course/", {
      course_id: courseId,
      promo_code: promoCode
    });
    return response.data;
  }

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

  async getMyCourses(): Promise<Course[]> {
    const response = await catalogApi.get("/v1/public/my-courses/");
    return response.data;
  }
}

export default new CourseService();
