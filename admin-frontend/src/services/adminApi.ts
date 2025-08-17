// admin-frontend/src/services/adminApi.ts

import api from '../api/axiosInstance';
import { z } from 'zod';

const CourseSchema = z.object({
  id: z.number().int().positive(),
  title: z.string(),
  short_description: z.string().nullable().optional(),
  full_description: z.string().nullable().optional(),
  image: z.string().nullable().optional(), // ← ИСПРАВЛЕНО: может быть null
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
}).passthrough();

export type AdminCourse = z.infer<typeof CourseSchema>;

export const getCoursesSafe = async (): Promise<AdminCourse[]> => {
  const { data } = await api.get('/admin/courses/');
  return z.array(CourseSchema).parse(data);
};


// ==================== КУРСЫ ====================
export const coursesApi = {
  // Получить список курсов
  getCourses: async () => {
  const { data } = await api.get('/admin/courses/');
  return data; // ← убрать .parse(data)
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
  }
};

// ==================== МОДУЛИ ====================
export const modulesApi = {
  // Получить модули курса
  getCourseModules: async (courseId: number) => {
    const response = await api.get(`/admin/courses/${courseId}/modules/`);
    return response.data;
  },

  // Создать модуль
  createModule: async (courseId: number, data: {
    title: string;
    group_title?: string;
    order?: number;
    sp_award?: number;
  }) => {
    const response = await api.post(`/admin/courses/${courseId}/module`, data);
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
  }
};

// ==================== БЛОКИ ====================
export const blocksApi = {
  // Получить блоки модуля
  getModuleBlocks: async (moduleId: number) => {
    const response = await api.get(`/admin/modules/${moduleId}/blocks`);
    return response.data;
  },

  // Создать блок
  createBlock: async (moduleId: number, data: {
    type: 'text' | 'video' | 'code' | 'image'
    title: string;
    content: string;
    order?: number;
    language?: string;
    video_preview?: string;
  }) => {
    const response = await api.post(`/admin/modules/${moduleId}/blocks`, data);
    return response.data;
  },

  // Получить блок
  getBlock: async (blockId: number) => {
    const response = await api.get(`/admin/blocks/${blockId}`);
    return response.data;
  },

  // Обновить блок
  updateBlock: async (blockId: number, data: any) => {
    const response = await api.put(`/admin/blocks/${blockId}`, data);
    return response.data;
  },

  // Удалить блок
  deleteBlock: async (blockId: number) => {
    const response = await api.delete(`/admin/blocks/${blockId}`);
    return response.data;
  },

  // Изменить порядок блоков
  reorderBlocks: async (moduleId: number, blocksOrder: Array<{id: number, order: number}>) => {
    const response = await api.post('/admin/blocks/reorder/', {
      module_id: moduleId,
      blocks_order: blocksOrder
    });
    return response.data;
  }
};

// ==================== БАННЕРЫ ====================
export const bannersApi = {
  // Получить список баннеров
  getBanners: async () => {
    const response = await api.get('/admin/banners/');
    return response.data;
  },

  // Получить баннер
  getBanner: async (id: number) => {
    const response = await api.get(`/admin/banners/${id}`);
    return response.data;
  },

  // Создать баннер
  createBanner: async (data: {
    image: string;
    order?: number;
    link?: string;
  }) => {
    const response = await api.post('/admin/banners/', data);
    return response.data;
  },

  // Обновить баннер
  updateBanner: async (id: number, data: any) => {
    const response = await api.put(`/admin/banners/${id}`, data);
    return response.data;
  },

  // Удалить баннер
  deleteBanner: async (id: number) => {
    const response = await api.delete(`/admin/banners/${id}`);
    return response.data;
  },

  // Изменить порядок баннеров
  reorderBanners: async (orderMap: Record<number, number>) => {
    const response = await api.post('/admin/banners/reorder/', {
      order_map: orderMap
    });
    return response.data;
  }
};

// ==================== МОДАЛЬНЫЕ ОКНА КУРСОВ ====================
export const courseModalApi = {
  // Получить модальное окно курса
  getModal: async (courseId: number) => {
    const response = await api.get(`/admin/course-extras/modal/${courseId}`);
    return response.data;
  },

  // Создать модальное окно
  createModal: async (courseId: number, data: {
    title: string;
    blocks: Array<{
      type: 'text' | 'image';
      content: string;
      order: number;
    }>;
  }) => {
    const response = await api.post(`/admin/course-extras/modal/${courseId}`, data);
    return response.data;
  },

  // Обновить модальное окно
  updateModal: async (courseId: number, data: {
    title?: string;
    blocks?: Array<{
      type: 'text' | 'image';
      content: string;
      order: number;
    }>;
  }) => {
    const response = await api.put(`/admin/course-extras/modal/${courseId}`, data);
    return response.data;
  },

  // Удалить модальное окно
  deleteModal: async (courseId: number) => {
    const response = await api.delete(`/admin/course-extras/modal/${courseId}`);
    return response.data;
  }
};

// ==================== РАБОТЫ УЧЕНИКОВ ====================
export const studentWorksApi = {
  // Получить работы учеников
  getWorks: async (courseId: number) => {
    const response = await api.get(`/admin/course-extras/student-works/${courseId}`);
    return response.data;
  },

  // Создать секцию работ
  createWorks: async (courseId: number, data: {
    title: string;
    description: string;
    works: Array<{
      image: string;
      description: string;
      bot_tag?: string;
      order: number;
    }>;
  }) => {
    const response = await api.post(`/admin/course-extras/student-works/${courseId}`, data);
    return response.data;
  },

  // Обновить секцию работ
  updateWorks: async (courseId: number, data: {
    title?: string;
    description?: string;
    works?: Array<{
      image: string;
      description: string;
      bot_tag?: string;
      order: number;
    }>;
  }) => {
    const response = await api.put(`/admin/course-extras/student-works/${courseId}`, data);
    return response.data;
  },

  // Удалить секцию работ
  deleteWorks: async (courseId: number) => {
    const response = await api.delete(`/admin/course-extras/student-works/${courseId}`);
    return response.data;
  }
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
      params: { days }
    });
    return response.data;
  },

  // Статистика курсов
  getCoursesStats: async (days: number = 30) => {
    const response = await api.get('/admin/statistics/courses/', {
      params: { days }
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
  }
};

// ==================== ПОЛЬЗОВАТЕЛИ ====================
export const usersApi = {
  // Получить список пользователей
  getUsers: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
  }) => {
    const response = await api.get('/admin/users/', { params });
    return response.data;
  },

  // Получить пользователя
  getUser: async (userId: number) => {
    const response = await api.get(`/admin/users/${userId}`);
    return response.data;
  },

  // Обновить пользователя
  updateUser: async (userId: number, data: any) => {
    const response = await api.put(`/admin/users/${userId}`, data);
    return response.data;
  },

  // Предоставить доступ к курсу
  grantCourseAccess: async (userId: number, courseId: number) => {
    const response = await api.post(`/admin/users/${userId}/grant-course/`, {
      course_id: courseId
    });
    return response.data;
  },

  // Отозвать доступ к курсу
  revokeCourseAccess: async (userId: number, courseId: number) => {
    const response = await api.post(`/admin/users/${userId}/revoke-course/`, {
      course_id: courseId
    });
    return response.data;
  }
};

// ==================== ЗАГРУЗКА ФАЙЛОВ ====================
// ==================== ЗАГРУЗКА ФАЙЛОВ ====================
export const uploadApi = {
  // Загрузить изображение
  uploadImage: async (file: File, folder: string = 'images') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder);

    const response = await api.post('/admin/upload/public/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
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
      timeout: 0
    });

    const videoId = data.video_id;

    // ждём обработки
    let status;
    do {
      await new Promise(r => setTimeout(r, 5000));
      status = (await api.get(`/admin/video-status/${videoId}`)).data;
    } while (status.status !== 'completed' && status.status !== 'failed');

    if (status.status === 'completed') {
      return status.result.master_playlist_url; // вернём HLS URL
    } else {
      throw new Error(status.error || 'Ошибка обработки видео');
    }
  }
};


// ==================== МАССОВЫЕ ОПЕРАЦИИ ====================
export const bulkOperationsApi = {
  // Массовые операции с курсами
  bulkCourses: async (operation: string, ids: number[], params?: any) => {
    const response = await api.post('/admin/bulk-operations/courses/', {
      operation,
      ids,
      params
    });
    return response.data;
  },

  // Массовые операции с модулями
  bulkModules: async (operation: string, ids: number[], params?: any) => {
    const response = await api.post('/admin/bulk-operations/modules/', {
      operation,
      ids,
      params
    });
    return response.data;
  },

  // Массовые операции с блоками
  bulkBlocks: async (operation: string, ids: number[], params?: any) => {
    const response = await api.post('/admin/bulk-operations/blocks/', {
      operation,
      ids,
      params
    });
    return response.data;
  }
};