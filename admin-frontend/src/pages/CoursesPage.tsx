//pages/CoursePage.tsx

import { useState, useEffect } from 'react';
import { Title, Container } from '@mantine/core';
import { EnhancedCourseTable } from '../components/EnhancedCourseTable';
import { coursesApi } from '../services/adminApi';
import Layout from '../components/Layout';

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

export default function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const data = await coursesApi.getCourses();
      setCourses(data);
    } catch (error) {
      console.error('Ошибка при получении курсов:', error);
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