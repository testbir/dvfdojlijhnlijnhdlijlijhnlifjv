// pages/CoursesPage.tsx

import { useState, useEffect } from 'react';
import { Title, Container } from '@mantine/core';
import { EnhancedCourseTable } from '../components/EnhancedCourseTable';
import { coursesApi, type AdminCourse } from '../services/adminApi';
import Layout from '../components/Layout';

export default function CoursesPage() {
  const [courses, setCourses] = useState<AdminCourse[]>([]);
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