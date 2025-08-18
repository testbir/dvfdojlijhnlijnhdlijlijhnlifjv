// src/components/EnhancedCourseTable.tsx

import { useState, useEffect } from 'react';
import { 
  Table, 
  Checkbox, 
  Group, 
  Button, 
  Image, 
  rem, 
  Title, 
  Badge,
  Text,
  ActionIcon,
  Menu
} from '@mantine/core';
import { Link } from 'react-router-dom';
import { IconDots, IconTrash, IconEye, IconCopy } from '@tabler/icons-react';
import { BulkOperations } from './BulkOperations';
import { type AdminCourse, coursesApi, bannersApi } from '../services/adminApi';

interface Banner {
  id: number;
  image: string;
  order: number;
  link?: string;
}

export function EnhancedCourseTable({ courses: initialCourses }: { courses: AdminCourse[] }) {
  const [courses, setCourses] = useState<AdminCourse[]>(initialCourses);
  const [banners, setBanners] = useState<Banner[]>([]);
  const [selectedCourses, setSelectedCourses] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setCourses(initialCourses);
  }, [initialCourses]);

  useEffect(() => {
    fetchBanners();
  }, []);

  const fetchBanners = async () => {
    try {
      const data = await bannersApi.getBanners();
      setBanners(data);
    } catch (e) {
      console.error('Ошибка при загрузке баннеров', e);
    }
  };

  const toggleSelection = (courseId: number) => {
    setSelectedCourses(prev =>
      prev.includes(courseId)
        ? prev.filter(id => id !== courseId)
        : [...prev, courseId]
    );
  };

  const selectAll = () => {
    if (selectedCourses.length === courses.length) {
      setSelectedCourses([]);
    } else {
      setSelectedCourses(courses.map(c => c.id));
    }
  };

  const handleDeleteBanner = async (id: number) => {
    if (!window.confirm('Удалить баннер?')) return;
    try {
      await bannersApi.deleteBanner(id);
      setBanners((prev) => prev.filter((b) => b.id !== id));
    } catch (e) {
      console.error('Ошибка удаления баннера', e);
    }
  };

  const handleDeleteCourse = async (id: number) => {
    if (!window.confirm('Удалить курс?')) return;
    try {
      await coursesApi.deleteCourse(id);
      setCourses(prev => prev.filter(c => c.id !== id));
      setSelectedCourses(prev => prev.filter(courseId => courseId !== id));
    } catch (e) {
      console.error('Ошибка удаления курса', e);
    }
  };

  const handleDuplicateCourse = async (courseId: number) => {
    try {
      setLoading(true);
      const original = courses.find(c => c.id === courseId);
      if (!original) return;

      await coursesApi.createCourse({
        ...original,
        id: undefined,
        title: `${original.title} (копия)`
      });

      const updatedCourses = await coursesApi.getCourses();
      setCourses(updatedCourses);
    } finally {
      setLoading(false);
    }
  };


  const refreshCourses = async () => {
    try {
      const data = await coursesApi.getCourses();
      setCourses(data);
    } catch (e) {
      console.error('Ошибка обновления курсов', e);
    }
  };

  return (
    <>
      <Group justify="space-between" mb="lg">
        <Group>
          <Button component={Link} to="/courses/create">Создать курс</Button>
          <Button component={Link} to="/banners/create" color="gray">Добавить баннер</Button>
          {selectedCourses.length > 0 && (
            <BulkOperations
              selectedItems={selectedCourses}
              itemType="courses"
              onComplete={() => {
                setSelectedCourses([]);
                refreshCourses();
              }}
            />
          )}
        </Group>
        {selectedCourses.length > 0 && (
          <Badge size="lg" variant="filled">
            Выбрано: {selectedCourses.length}
          </Badge>
        )}
      </Group>

      {/* === Баннеры === */}
      <Title order={3} mt="md" mb="sm">Баннеры</Title>
      <Table withRowBorders withColumnBorders highlightOnHover mb="xl">
        <Table.Thead>
          <Table.Tr>
            <Table.Th>ID</Table.Th>
            <Table.Th>Изображение</Table.Th>
            <Table.Th>Порядок</Table.Th>
            <Table.Th>Ссылка</Table.Th>
            <Table.Th style={{ width: rem(180) }}>Действия</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {banners.sort((a, b) => a.order - b.order).map((banner) => (
            <Table.Tr key={`banner-${banner.id}`} style={{ backgroundColor: '#f6f6f6' }}>
              <Table.Td>{banner.id}</Table.Td>
              <Table.Td>
                <Image src={banner.image} width={120} radius="sm" />
              </Table.Td>
              <Table.Td>{banner.order}</Table.Td>
              <Table.Td>
                {banner.link ? (
                  <Text size="sm" truncate style={{ maxWidth: 200 }}>
                    {banner.link}
                  </Text>
                ) : (
                  <Text size="sm" c="dimmed">Нет ссылки</Text>
                )}
              </Table.Td>
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
            <Table.Th style={{ width: 40 }}>
              <Checkbox
                checked={selectedCourses.length === courses.length && courses.length > 0}
                indeterminate={selectedCourses.length > 0 && selectedCourses.length < courses.length}
                onChange={selectAll}
              />
            </Table.Th>
            <Table.Th>ID</Table.Th>
            <Table.Th>Превью</Table.Th>
            <Table.Th>Название</Table.Th>
            <Table.Th>Тип</Table.Th>
            <Table.Th>Цена</Table.Th>
            <Table.Th>Скидка</Table.Th>
            <Table.Th>Порядок</Table.Th>
            <Table.Th style={{ width: rem(200) }}>Действия</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {[...courses].sort((a, b) => (a.order ?? 0) - (b.order ?? 0)).map((course) => (
            <Table.Tr key={`course-${course.id}`}>
              <Table.Td>
                <Checkbox
                  checked={selectedCourses.includes(course.id)}
                  onChange={() => toggleSelection(course.id)}
                />
              </Table.Td>
              <Table.Td>{course.id}</Table.Td>
              <Table.Td>
                {course.image ? (
                  <Image src={course.image} width={60} height={40} radius="sm" fit="cover" />
                ) : (
                  <Text size="xs" c="dimmed">Нет изображения</Text>
                )}
              </Table.Td>
              <Table.Td>
                <Text fw={500}>{course.title}</Text>
                {course.short_description && (
                  <Text size="xs" c="dimmed" truncate style={{ maxWidth: 300 }}>
                    {course.short_description}
                  </Text>
                )}
              </Table.Td>
              <Table.Td>
                <Badge color={course.is_free ? 'green' : 'blue'}>
                  {course.is_free ? 'Бесплатный' : 'Платный'}
                </Badge>
              </Table.Td>
              <Table.Td>
                {course.is_free ? (
                  <Text c="dimmed">—</Text>
                ) : (
                  <Text>{course.price} ₽</Text>
                )}
              </Table.Td>
              <Table.Td>
                {!course.is_free && course.discount && course.discount > 0 && course.is_discount_active ? (
                  <Badge color="red" variant="light">
                    -{course.discount}%
                  </Badge>
                ) : (
                  <Text c="dimmed">—</Text>
                )}
              </Table.Td>
              <Table.Td>{course.order ?? 0}</Table.Td>
              <Table.Td>
                <Group gap="xs">
                  <Button 
                    component={Link} 
                    to={`/courses/${course.id}/structure`} 
                    size="xs" 
                    variant="light"
                  >
                    Структура
                  </Button>
                  <Button 
                    component={Link} 
                    to={`/courses/${course.id}/edit`} 
                    size="xs" 
                    variant="light"
                  >
                    Редактировать
                  </Button>
                  <Menu shadow="md" width={200}>
                    <Menu.Target>
                      <ActionIcon variant="light" size="sm">
                        <IconDots size={16} />
                      </ActionIcon>
                    </Menu.Target>
                    <Menu.Dropdown>
                      <Menu.Item
                        leftSection={<IconEye size={14} />}
                        component="a"
                        href={`http://localhost:5173/courses/${course.id}`}
                        target="_blank"
                      >
                        Предпросмотр
                      </Menu.Item>
                      <Menu.Item
                        leftSection={<IconCopy size={14} />}
                        onClick={() => handleDuplicateCourse(course.id)}
                        disabled={loading}
                      >
                        Дублировать
                      </Menu.Item>
                      <Menu.Divider />
                      <Menu.Item
                        color="red"
                        leftSection={<IconTrash size={14} />}
                        onClick={() => handleDeleteCourse(course.id)}
                      >
                        Удалить
                      </Menu.Item>
                    </Menu.Dropdown>
                  </Menu>
                </Group>
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </>
  );
}