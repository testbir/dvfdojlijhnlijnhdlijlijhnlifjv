// admin-frontend/src/services/adminApi.ts

import api from '../api/axiosInstance';
import { z } from 'zod';

const CourseSchema = z.object({
  id: z.number().int().positive(),
  title: z.string(),
  short_description: z.string().nullable().optional(),
  full_description: z.string().nullable().optional(),
  image: z.string().nullable(),
  is_free: z.boolean().optional().default(false),
  price: z.number().nonnegative().nullable().optional(),
  discount: z.number().nonnegative().nullable().optional(),
  video: z.string().nullable().optional(),
  video_preview: z.string().nullable().optional(),
  banner_text: z.string().nullable().optional(),
  banner_color_left: z.string().nullable().optional(),
  banner_color_right: z.string().nullable().optional(),
  order: z.number().int().nonnegative().nullable().optional(),
  discount_start: z.string().nullable().optional(),
  discount_until: z.string().nullable().optional(),
  group_title: z.string().nullable().optional(),
  is_discount_active: z.boolean().optional(),
}).passthrough();

export type AdminCourse = z.infer<typeof CourseSchema>;

export const getCoursesSafe = async (): Promise<AdminCourse[]> => {
  const { data } = await api.get('/admin/courses/');
  return z.array(CourseSchema).parse(data);
};

// ==================== КУРСЫ ====================
export const coursesApi = {
  // Получить список курсов
  getCourses: async (): Promise<AdminCourse[]> => {
    const { data } = await api.get('/admin/courses/');
    console.log('Raw data from API:', data);
    return z.array(CourseSchema).parse(data);
  },
  // Получить курс по ID
  getCourse: async (id: number) => {
    const response = await api.get(`/admin/courses/${id}`);
    return response.data;
  },

  // Создать курс
  createCourse: async (data: any) => {
    const response = await api.post('/admin/courses/', data);
    return response.data;
  },

  // Обновить курс
  updateCourse: async (id: number, data: any) => {
    const response = await api.put(`/admin/courses/${id}`, data);
    return response.data;
  },

  // Удалить курс
  deleteCourse: async (id: number) => {
    await api.delete(`/admin/courses/${id}`);
    return { success: true };
  },
};

// ==================== МОДУЛИ ====================
export const modulesApi = {
  // Получить модули курса
  getCourseModules: async (courseId: number) => {
    const response = await api.get(`/admin/courses/${courseId}/modules/`);
    return response.data;
  },

  // Создать модуль
  createModule: async (
    courseId: number,
    data: {
      title: string;
      group_title?: string;
      order?: number;
      sp_award?: number;
    }
  ) => {
    const response = await api.post(`/admin/courses/${courseId}/modules/`, data);
    return response.data;
  },

  // Получить модуль
  getModule: async (moduleId: number) => {
    const response = await api.get(`/admin/modules/${moduleId}`);
    return response.data;
  },

  // Обновить модуль
  updateModule: async (moduleId: number, data: any) => {
    const response = await api.put(`/admin/modules/${moduleId}`, data);
    return response.data;
  },

  // Удалить модуль
  deleteModule: async (moduleId: number) => {
    const response = await api.delete(`/admin/modules/${moduleId}`);
    return response.data;
  },
};

// ==================== БЛОКИ ====================
export const blocksApi = {
  // Получить блоки модуля (коллекция → со слэшем)
  getModuleBlocks: async (moduleId: number) => {
    const response = await api.get(`/admin/modules/${moduleId}/blocks/`);
    return response.data;
  },

  // Создать блок (коллекция → со слэшем)
  createBlock: async (
    moduleId: number,
    data: {
      type: 'text' | 'video' | 'code' | 'image';
      title: string;
      content: string;
      order?: number;
      language?: string;
      video_preview?: string;
    }
  ) => {
    const response = await api.post(`/admin/modules/${moduleId}/blocks/`, data);
    return response.data;
  },

  // Получить блок (элемент → без слэша)
  getBlock: async (blockId: number) => {
    const response = await api.get(`/admin/blocks/${blockId}`);
    return response.data;
  },

  // Обновить блок (элемент → без слэша)
  updateBlock: async (blockId: number, data: any) => {
    const response = await api.put(`/admin/blocks/${blockId}`, data);
    return response.data;
  },

  // Удалить блок (элемент → без слэша)
  deleteBlock: async (blockId: number) => {
    const response = await api.delete(`/admin/blocks/${blockId}`);
    return response.data;
  },

  // Изменить порядок блоков
  reorderBlocks: async (moduleId: number, blocksOrder: Array<{ id: number; order: number }>) => {
    const response = await api.post('/admin/blocks/reorder/', {
      module_id: moduleId,
      blocks_order: blocksOrder,
    });
    return response.data;
  },
};

// ==================== БАННЕРЫ ====================
// ==================== БАННЕРЫ ====================
export const bannersApi = {
  getBanners: async () => (await api.get('/admin/banners/')).data,

  getBanner: async (id: number) =>
    (await api.get(`/admin/banners/${id}`)).data,

  // <-- принимает FormData
  createBanner: async (form: FormData) =>
    (await api.post('/admin/banners/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })).data,

  // <-- тоже FormData (поддержка смены файла)
  updateBanner: async (id: number, form: FormData) =>
    (await api.put(`/admin/banners/${id}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })).data,

  deleteBanner: async (id: number) =>
    (await api.delete(`/admin/banners/${id}`)).data,

  reorderBanners: async (orderMap: Record<number, number>) =>
    (await api.post('/admin/banners/reorder/', { order_map: orderMap })).data,
};

// ==================== МОДАЛЬНЫЕ ОКНА КУРСОВ ====================
export const courseModalApi = {
  // Получить модальное окно курса (элемент курса → без слэша)
  getModal: async (courseId: number) => {
    const response = await api.get(`/admin/course-extras/modal/${courseId}`);
    return response.data;
  },

  // Создать модальное окно (элемент курса → без слэша)
  createModal: async (
    courseId: number,
    data: {
      title: string;
      blocks: Array<{
        type: 'text' | 'image';
        content: string;
        order: number;
      }>;
    }
  ) => {
    const response = await api.post(`/admin/course-extras/modal/${courseId}`, data);
    return response.data;
  },

  // Обновить модальное окно (элемент курса → без слэша)
  updateModal: async (
    courseId: number,
    data: {
      title?: string;
      blocks?: Array<{
        type: 'text' | 'image';
        content: string;
        order: number;
      }>;
    }
  ) => {
    const response = await api.put(`/admin/course-extras/modal/${courseId}`, data);
    return response.data;
  },

  // Удалить модальное окно (элемент курса → без слэша)
  deleteModal: async (courseId: number) => {
    const response = await api.delete(`/admin/course-extras/modal/${courseId}`);
    return response.data;
  },
};

// ==================== РАБОТЫ УЧЕНИКОВ ====================
export const studentWorksApi = {
  // Получить работы учеников (элемент курса → без слэша)
  getWorks: async (courseId: number) => {
    const response = await api.get(`/admin/course-extras/student-works/${courseId}`);
    return response.data;
  },

  // Создать секцию работ (элемент курса → без слэша)
  createWorks: async (
    courseId: number,
    data: {
      title: string;
      description: string;
      works: Array<{
        image: string;
        description: string;
        bot_tag?: string;
        order: number;
      }>;
    }
  ) => {
    const response = await api.post(`/admin/course-extras/student-works/${courseId}`, data);
    return response.data;
  },

  // Обновить секцию работ (элемент курса → без слэша)
  updateWorks: async (
    courseId: number,
    data: {
      title?: string;
      description?: string;
      works?: Array<{
        image: string;
        description: string;
        bot_tag?: string;
        order: number;
      }>;
    }
  ) => {
    const response = await api.put(`/admin/course-extras/student-works/${courseId}`, data);
    return response.data;
  },

  // Удалить секцию работ (элемент курса → без слэша)
  deleteWorks: async (courseId: number) => {
    const response = await api.delete(`/admin/course-extras/student-works/${courseId}`);
    return response.data;
  },
};

// ==================== СТАТИСТИКА ====================
export const statisticsApi = {
  // Общая статистика платформы
  getPlatformStats: async () => {
    const response = await api.get('/admin/statistics/');
    return response.data;
  },

  // Статистика пользователей
  getUsersStats: async (days: number = 30) => {
    const response = await api.get('/admin/statistics/users/', {
      params: { days },
    });
    return response.data;
  },

  // Статистика курсов
  getCoursesStats: async (days: number = 30) => {
    const response = await api.get('/admin/statistics/courses/', {
      params: { days },
    });
    return response.data;
  },

  // Статистика доходов
  getRevenueStats: async () => {
    const response = await api.get('/admin/statistics/revenue/');
    return response.data;
  },

  // Статистика обучения
  getLearningStats: async () => {
    const response = await api.get('/admin/statistics/learning/');
    return response.data;
  },
};

// ==================== ПОЛЬЗОВАТЕЛИ ====================
export const usersApi = {
  // Получить список пользователей
  getUsers: async (params?: { page?: number; limit?: number; search?: string }) => {
    const response = await api.get('/admin/users/', { params });
    return response.data;
  },

  // Получить пользователя (элемент → без слэша)
  getUser: async (userId: number) => {
    const response = await api.get(`/admin/users/${userId}`);
    return response.data;
  },

  // Обновить пользователя (элемент → без слэша)
  updateUser: async (userId: number, data: any) => {
    const response = await api.put(`/admin/users/${userId}`, data);
    return response.data;
  },

  // Предоставить доступ к курсу
  grantCourseAccess: async (userId: number, courseId: number) => {
    const response = await api.post(`/admin/users/${userId}/grant-course/`, {
      course_id: courseId,
    });
    return response.data;
  },

  // Отозвать доступ к курсу
  revokeCourseAccess: async (userId: number, courseId: number) => {
    const response = await api.post(`/admin/users/${userId}/revoke-course/`, {
      course_id: courseId,
    });
    return response.data;
  },
};

// ==================== ЗАГРУЗКА ФАЙЛОВ ====================
export const uploadApi = {
  // Загрузить изображение
  uploadImage: async (file: File, folder: string = 'images') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder);

    const response = await api.post('/admin/upload/public/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Загрузить и обработать видео (HLS)
  uploadVideo: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    // загружаем
    const { data } = await api.post('/admin/upload/video-public/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 0,
    });

    const videoId = data.video_id;

    // ждём обработки
    let status;
    do {
      await new Promise((r) => setTimeout(r, 5000));
      status = (await api.get(`/admin/video-status/${videoId}`)).data;
    } while (status.status !== 'completed' && status.status !== 'failed');

    if (status.status === 'completed') {
      return status.result.master_playlist_url;
    } else {
      throw new Error(status.error || 'Ошибка обработки видео');
    }
  },
};

// ==================== МАССОВЫЕ ОПЕРАЦИИ ====================
export const bulkOperationsApi = {
  // Массовые операции с курсами
  bulkCourses: async (operation: string, ids: number[], params?: any) => {
    const response = await api.post('/admin/bulk-operations/courses/', {
      operation,
      ids,
      params,
    });
    return response.data;
  },

  // Массовые операции с модулями
  bulkModules: async (operation: string, ids: number[], params?: any) => {
    const response = await api.post('/admin/bulk-operations/modules/', {
      operation,
      ids,
      params,
    });
    return response.data;
  },

  // Массовые операции с блоками
  bulkBlocks: async (operation: string, ids: number[], params?: any) => {
    const response = await api.post('/admin/bulk-operations/blocks/', {
      operation,
      ids,
      params,
    });
    return response.data;
  },
};


export const promoCodesApi = {
  getPromoCodes: async () => {
    const { data } = await api.get('/admin/promocodes/');
    return data;
  },
  createPromoCode: async (payload: any) => {
    const { data } = await api.post('/admin/promocodes/', payload);
    return data;
  },
  updatePromoCode: async (id: number, payload: any) => {
    const { data } = await api.put(`/admin/promocodes/${id}`, payload);
    return data;
  },
  deletePromoCode: async (id: number) => {
    const { data } = await api.delete(`/admin/promocodes/${id}`);
    return data;
  },
};