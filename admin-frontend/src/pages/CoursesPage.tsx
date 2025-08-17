// pages/CoursesPage.tsx
import { useState, useEffect } from 'react';
import { Title, Container } from '@mantine/core';
import { EnhancedCourseTable } from '../components/EnhancedCourseTable';
import { coursesApi } from '../services/adminApi';
import Layout from '../components/Layout';
import { z } from 'zod';

interface Course {
  id: number;
  title: string;
  price: number;
  order?: number;
  is_free: boolean;
  discount?: number;
  image?: string;
  short_description?: string;
}

// схема ответа бэка
const ApiCourse = z.object({
  id: z.number().int().positive(),
  title: z.string(),
  is_free: z.boolean(),
  price: z.number().nonnegative().optional(),
  order: z.number().int().nonnegative().optional(),
  discount: z.number().nonnegative().optional(),
  image: z.string().optional(),
  short_description: z.string().optional(),
  is_discount_active: z.boolean().optional(),
});
const ApiCourses = z.array(ApiCourse);

export default function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { void fetchCourses(); }, []);

  const fetchCourses = async () => {
    try {
      const raw = await coursesApi.getCourses(); // что угодно с бэка
      const parsed = ApiCourses.safeParse(raw);
      if (!parsed.success) {
        console.error('Невалидный ответ /admin/courses/', parsed.error);
        setCourses([]);
        return;
      }
      // нормализация под таблицу
      const normalized: Course[] = parsed.data
        .filter(c => Number.isSafeInteger(c.id) && c.id > 0)
        .map(c => ({
          id: c.id,
          title: c.title,
          is_free: c.is_free,
          price: c.is_free ? 0 : (typeof c.price === 'number' ? c.price : 0),
          order: c.order ?? 0,
          discount: c.discount,
          image: c.image,
          short_description: c.short_description,
        }));
      setCourses(normalized);
    } catch (error) {
      console.error('Ошибка при получении курсов:', error);
      setCourses([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Container fluid px="xl">
        <Title order={2} ta="center" mb="lg">Управление курсами</Title>
        {!loading && <EnhancedCourseTable courses={courses} />}
      </Container>
    </Layout>
  );
}
