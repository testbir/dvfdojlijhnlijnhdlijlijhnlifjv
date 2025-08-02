//components/CourseTable.tsx


import { Table, Button, Group, Image, rem, Title } from '@mantine/core';
import { Link } from 'react-router-dom';
import api from '../api/axiosInstance';
import { useEffect, useState } from 'react';

interface Course {
  id: number;
  title: string;
  price: number;
  order?: number;
}

interface Banner {
  id: number;
  image: string;
  order: number;
}

export default function CourseTable({ courses }: { courses: Course[] }) {
  const [banners, setBanners] = useState<Banner[]>([]);

  const fetchBanners = async () => {
    try {
      const res = await api.get('/admin/banners/');
      setBanners(res.data);
    } catch (e) {
      console.error('Ошибка при загрузке баннеров', e);
    }
  };

  useEffect(() => {
    fetchBanners();
  }, []);

  const handleDeleteBanner = async (id: number) => {
    if (!window.confirm('Удалить баннер?')) return;
    try {
      await api.delete(`/admin/banners/${id}`);
      setBanners((prev) => prev.filter((b) => b.id !== id));
    } catch (e) {
      console.error('Ошибка удаления баннера', e);
    }
  };

  return (
    <>
      <Group justify="space-between" mb="lg">
        <Button component={Link} to="/courses/create">Создать курс</Button>
        <Button component={Link} to="/banners/create" color="gray">Добавить баннер</Button>
      </Group>

      {/* === Баннеры === */}
      <Title order={3} mt="md" mb="sm">Баннеры</Title>
      <Table withRowBorders withColumnBorders highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>ID</Table.Th>
            <Table.Th>Изображение</Table.Th>
            <Table.Th>Порядок</Table.Th>
            <Table.Th style={{ width: rem(180) }}>Действия</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {banners.sort((a, b) => a.order - b.order).map((banner) => (
            <Table.Tr key={`banner-${banner.id}`} style={{ backgroundColor: '#f6f6f6' }}>
              <Table.Td>{banner.id}</Table.Td>
              <Table.Td><Image src={banner.image} width={120} radius="sm" /></Table.Td>
              <Table.Td>{banner.order}</Table.Td>
              <Table.Td>
                <Group gap="xs">
                  <Button
                    component={Link}
                    to={`/banners/${banner.id}`}
                    size="xs"
                    variant="light"
                  >
                    Редактировать
                  </Button>
                  <Button
                    color="red"
                    size="xs"
                    variant="light"
                    onClick={() => handleDeleteBanner(banner.id)}
                  >
                    Удалить
                  </Button>
                </Group>
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>

      {/* === Курсы === */}
      <Title order={3} mt="xl" mb="sm">Курсы</Title>
      <Table withRowBorders withColumnBorders highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>ID</Table.Th>
            <Table.Th>Название</Table.Th>
            <Table.Th>Цена</Table.Th>
            <Table.Th>Порядок</Table.Th>
            <Table.Th style={{ width: rem(180) }}>Действия</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {[...courses].sort((a, b) => (a.order ?? 0) - (b.order ?? 0)).map((course) => (
            <Table.Tr key={`course-${course.id}`}>
              <Table.Td>{course.id}</Table.Td>
              <Table.Td>{course.title}</Table.Td>
              <Table.Td>{course.price} ₽</Table.Td>
              <Table.Td>{course.order ?? 0}</Table.Td>
              <Table.Td>
                <Group gap="xs">
                  <Button component={Link} to={`/courses/${course.id}/structure`} size="xs" variant="light">
                    Структура
                  </Button>
                  <Button component={Link} to={`/courses/${course.id}/edit`} size="xs" variant="light">
                    Редактировать
                  </Button>
                  <Button
                    color="red"
                    size="xs"
                    variant="light"
                    onClick={async () => {
                      if (window.confirm("Удалить курс?")) {
                        await api.delete(`/admin/courses/${course.id}`);
                        window.location.reload();
                      }
                    }}
                  >
                    Удалить
                  </Button>
                </Group>
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </>
  );
}
