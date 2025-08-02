// pages/CourseStructurePage.tsx

import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axiosInstance';
import Layout from '../components/Layout';
import { 
  Container, 
  Title, 
  Button, 
  Table, 
  Group, 
  Loader, 
  Center, 
  Notification,
  Paper,
  Text,
  Stack,
  Badge,
  Alert
} from '@mantine/core';
import { 
  IconWindow, 
  IconUsers, 
  IconPlus,
  IconEdit,
  IconCheck,
  IconX
} from '@tabler/icons-react';

interface Module {
  id: number;
  group_title: string | null;
  title: string;
  order: number;
}

interface CourseExtras {
  hasModal: boolean;
  hasStudentWorks: boolean;
}

export default function CourseStructurePage() {
  const { courseId } = useParams<{ courseId: string }>();
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [extras, setExtras] = useState<CourseExtras>({ hasModal: false, hasStudentWorks: false });

  useEffect(() => {
    fetchData();
  }, [courseId]);

  const fetchData = async () => {
    try {
      // Загружаем модули
      const modulesRes = await api.get(`/admin/courses/${courseId}/modules/`);
      setModules(modulesRes.data);

      // Проверяем наличие модального окна и работ учеников
      try {
        const modalRes = await api.get(`/admin/course-extras/modal/${courseId}/`);
        const worksRes = await api.get(`/admin/course-extras/student-works/${courseId}/`);
        
        setExtras({
          hasModal: !!modalRes.data,
          hasStudentWorks: !!worksRes.data
        });
      } catch (err) {
        // Если ошибка 404, значит элементов нет, это нормально
        console.log('Дополнительные элементы не найдены');
      }
    } catch (err) {
      setError('Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteModule = async (moduleId: number) => {
    if (!window.confirm("Вы уверены, что хотите удалить модуль?")) return;

    try {
      await api.delete(`/admin/modules/${moduleId}`);
      setModules(modules.filter(m => m.id !== moduleId));
    } catch (err) {
      setError('Ошибка при удалении модуля');
    }
  };

  return (
    <Layout>
      <Container>
        <Title order={2} ta="center" mb="lg">Структура курса</Title>

        {error && (
          <Notification color="red" mb="md">{error}</Notification>
        )}

        {/* Секция дополнительных элементов */}
        <Paper p="md" mb="xl" withBorder>
          <Title order={4} mb="md">Дополнительные элементы курса</Title>
          
          <Stack gap="md">
            <Group>
              <Paper p="sm" withBorder style={{ flex: 1 }}>
                <Group justify="space-between">
                  <Group>
                    <IconWindow size={24} />
                    <div>
                      <Text fw={500}>Модальное окно</Text>
                      <Text size="sm" c="dimmed">
                        Показывается при открытии курса
                      </Text>
                    </div>
                  </Group>
                  <Group>
                    {extras.hasModal ? (
                      <>
                        <Badge color="green" leftSection={<IconCheck size={14} />}>
                          Добавлено
                        </Badge>
                        <Button 
                          component={Link} 
                          to={`/courses/${courseId}/modal`}
                          size="sm"
                          variant="light"
                          leftSection={<IconEdit size={16} />}
                        >
                          Редактировать
                        </Button>
                      </>
                    ) : (
                      <>
                        <Badge color="gray" leftSection={<IconX size={14} />}>
                          Не добавлено
                        </Badge>
                        <Button 
                          component={Link} 
                          to={`/courses/${courseId}/modal`}
                          size="sm"
                          leftSection={<IconPlus size={16} />}
                        >
                          Добавить
                        </Button>
                      </>
                    )}
                  </Group>
                </Group>
              </Paper>
            </Group>

            <Group>
              <Paper p="sm" withBorder style={{ flex: 1 }}>
                <Group justify="space-between">
                  <Group>
                    <IconUsers size={24} />
                    <div>
                      <Text fw={500}>Работы учеников</Text>
                      <Text size="sm" c="dimmed">
                        Примеры проектов студентов
                      </Text>
                    </div>
                  </Group>
                  <Group>
                    {extras.hasStudentWorks ? (
                      <>
                        <Badge color="green" leftSection={<IconCheck size={14} />}>
                          Добавлено
                        </Badge>
                        <Button 
                          component={Link} 
                          to={`/courses/${courseId}/student-works`}
                          size="sm"
                          variant="light"
                          leftSection={<IconEdit size={16} />}
                        >
                          Редактировать
                        </Button>
                      </>
                    ) : (
                      <>
                        <Badge color="gray" leftSection={<IconX size={14} />}>
                          Не добавлено
                        </Badge>
                        <Button 
                          component={Link} 
                          to={`/courses/${courseId}/student-works`}
                          size="sm"
                          leftSection={<IconPlus size={16} />}
                        >
                          Добавить
                        </Button>
                      </>
                    )}
                  </Group>
                </Group>
              </Paper>
            </Group>
          </Stack>
        </Paper>

        {/* Секция модулей */}
        <Group justify="space-between" mb="lg">
          <Title order={4}>Модули курса</Title>
          <Button component={Link} to={`/courses/${courseId}/modules/create`}>
            Добавить модуль
          </Button>
        </Group>

        {loading ? (
          <Center><Loader /></Center>
        ) : modules.length === 0 ? (
          <Alert color="blue">
            В этом курсе пока нет модулей. Нажмите "Добавить модуль", чтобы создать первый.
          </Alert>
        ) : (
          <Table withRowBorders withColumnBorders highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Группа</Table.Th>
                <Table.Th>Модуль</Table.Th>
                <Table.Th>Порядок</Table.Th>
                <Table.Th>Действия</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {modules.map((mod) => (
                <Table.Tr key={mod.id}>
                  <Table.Td>{mod.group_title || '-'}</Table.Td>
                  <Table.Td>{mod.title}</Table.Td>
                  <Table.Td>{mod.order}</Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      <Button component={Link} to={`/modules/${mod.id}/blocks`} size="xs">
                        Блоки
                      </Button>
                      <Button component={Link} to={`/modules/${mod.id}/edit`} size="xs" variant="light">
                        Редактировать
                      </Button>
                      <Button color="red" size="xs" onClick={() => handleDeleteModule(mod.id)}>
                        Удалить
                      </Button>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Container>
    </Layout>
  );
}