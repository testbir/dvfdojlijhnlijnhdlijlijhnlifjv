// admin-frontend/src/pages/CoursesPage.tsx

import { useState, useEffect } from 'react';
import { Title, Container, Alert, Loader, Center } from '@mantine/core';
import { EnhancedCourseTable } from '../components/EnhancedCourseTable';
import { getCoursesSafe, type AdminCourse } from '../services/adminApi';
import Layout from '../components/Layout';

export default function CoursesPage() {
  const [courses, setCourses] = useState<AdminCourse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Используем безопасную функцию загрузки
      const data = await getCoursesSafe();
      setCourses(data);
      
      console.log('Загружено курсов:', data.length);
    } catch (error) {
      console.error('Ошибка при получении курсов:', error);
      setError('Не удалось загрузить курсы. Проверьте консоль для подробностей.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Container fluid px="xl">
          <Center style={{ height: '50vh' }}>
            <Loader size="lg" />
          </Center>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container fluid px="xl">
        <Title order={2} ta="center" mb="lg">Управление курсами</Title>
        
        {error && (
          <Alert color="red" mb="lg">
            {error}
          </Alert>
        )}
        
        <EnhancedCourseTable courses={courses} />
      </Container>
    </Layout>
  );
}