// admin-frontend/src/pages/CourseStructurePage.tsx

import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
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
  Alert,
  ActionIcon,
  Card,
  Accordion
} from '@mantine/core';
import { 
  IconWindow, 
  IconUsers, 
  IconPlus,
  IconEdit,
  IconCheck,
  IconX,
  IconTrash,
  IconCoins,
  IconFolder
} from '@tabler/icons-react';
import { modulesApi, courseModalApi, studentWorksApi } from '../services/adminApi';

interface Module {
  id: number;
  group_title: string | null;
  title: string;
  order: number;
  sp_award?: number;
}

interface CourseExtras {
  hasModal: boolean;
  hasStudentWorks: boolean;
}

interface GroupedModules {
  [key: string]: Module[];
}

export default function CourseStructurePage() {
  const { courseId } = useParams<{ courseId: string }>();
  const [modules, setModules] = useState<Module[]>([]);
  const [groupedModules, setGroupedModules] = useState<GroupedModules>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [extras, setExtras] = useState<CourseExtras>({ hasModal: false, hasStudentWorks: false });

  useEffect(() => {
    fetchData();
  }, [courseId]);

  const fetchData = async () => {
    if (!courseId) return;
    
    try {
      setLoading(true);
      
      // Загружаем модули
      const modulesData = await modulesApi.getCourseModules(Number(courseId));
      setModules(modulesData);
      
      // Группируем модули
      const grouped: GroupedModules = {};
      modulesData.forEach((module: Module) => {
        const groupKey = module.group_title || 'Без группы';
        if (!grouped[groupKey]) {
          grouped[groupKey] = [];
        }
        grouped[groupKey].push(module);
      });
      
      // Сортируем модули внутри групп
      Object.keys(grouped).forEach(key => {
        grouped[key].sort((a, b) => a.order - b.order);
      });
      
      setGroupedModules(grouped);

      // Проверяем наличие модального окна и работ учеников
      try {
        const [modalData, worksData] = await Promise.all([
          courseModalApi.getModal(Number(courseId)).catch(() => null),
          studentWorksApi.getWorks(Number(courseId)).catch(() => null)
        ]);
        
        setExtras({
          hasModal: !!modalData,
          hasStudentWorks: !!worksData
        });
      } catch (err) {
        console.log('Дополнительные элементы не найдены');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteModule = async (moduleId: number) => {
    if (!window.confirm("Вы уверены, что хотите удалить модуль? Все блоки модуля также будут удалены.")) {
      return;
    }

    try {
      await modulesApi.deleteModule(moduleId);
      setModules(modules.filter(m => m.id !== moduleId));
      
      // Обновляем группированные модули
      const newGrouped = { ...groupedModules };
      Object.keys(newGrouped).forEach(key => {
        newGrouped[key] = newGrouped[key].filter(m => m.id !== moduleId);
        if (newGrouped[key].length === 0) {
          delete newGrouped[key];
        }
      });
      setGroupedModules(newGrouped);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при удалении модуля');
    }
  };

  if (loading) {
    return (
      <Layout>
        <Center h="100vh">
          <Loader size="lg" />
        </Center>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container size="lg">
        <Title order={2} ta="center" mb="xl">Структура курса</Title>

        {error && (
          <Notification color="red" onClose={() => setError(null)} mb="md">
            {error}
          </Notification>
        )}

        {/* Секция дополнительных элементов */}
        <Paper p="md" mb="xl" withBorder>
          <Title order={4} mb="md">Дополнительные элементы курса</Title>
          
          <Stack gap="md">
            <Card shadow="sm" padding="lg" withBorder>
              <Group justify="space-between">
                <Group>
                  <IconWindow size={24} color="var(--mantine-color-blue-6)" />
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
            </Card>

            <Card shadow="sm" padding="lg" withBorder>
              <Group justify="space-between">
                <Group>
                  <IconUsers size={24} color="var(--mantine-color-green-6)" />
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
            </Card>
          </Stack>
        </Paper>

        {/* Секция модулей */}
        <Paper p="md" withBorder>
          <Group justify="space-between" mb="lg">
            <Title order={4}>Модули курса</Title>
            <Button 
              component={Link} 
              to={`/courses/${courseId}/modules/create`}
              leftSection={<IconPlus size={16} />}
            >
              Добавить модуль
            </Button>
          </Group>

          {modules.length === 0 ? (
            <Alert color="blue">
              В этом курсе пока нет модулей. Нажмите "Добавить модуль", чтобы создать первый.
            </Alert>
          ) : (
            <Accordion defaultValue={Object.keys(groupedModules)[0]}>
              {Object.entries(groupedModules).map(([groupName, groupModules]) => (
                <Accordion.Item key={groupName} value={groupName}>
                  <Accordion.Control icon={<IconFolder size={20} />}>
                    <Group justify="space-between">
                      <Text fw={500}>{groupName}</Text>
                      <Badge variant="light">{groupModules.length} модулей</Badge>
                    </Group>
                  </Accordion.Control>
                  <Accordion.Panel>
                    <Table>
                      <Table.Thead>
                        <Table.Tr>
                          <Table.Th>Порядок</Table.Th>
                          <Table.Th>Название</Table.Th>
                          <Table.Th>SP баллы</Table.Th>
                          <Table.Th>Действия</Table.Th>
                        </Table.Tr>
                      </Table.Thead>
                      <Table.Tbody>
                        {groupModules.map((module) => (
                          <Table.Tr key={module.id}>
                            <Table.Td width={80}>
                              <Badge variant="light">{module.order}</Badge>
                            </Table.Td>
                            <Table.Td>
                              <Text fw={500}>{module.title}</Text>
                            </Table.Td>
                            <Table.Td width={120}>
                              {module.sp_award ? (
                                <Badge 
                                  leftSection={<IconCoins size={14} />} 
                                  color="yellow"
                                >
                                  {module.sp_award} SP
                                </Badge>
                              ) : (
                                <Text size="sm" c="dimmed">—</Text>
                              )}
                            </Table.Td>
                            <Table.Td width={200}>
                              <Group gap="xs">
                                <Button
                                  component={Link}
                                  to={`/modules/${module.id}/blocks`}
                                  size="xs"
                                  variant="light"
                                >
                                  Блоки
                                </Button>
                                <Button
                                  component={Link}
                                  to={`/modules/${module.id}/edit`}
                                  size="xs"
                                  variant="light"
                                  color="blue"
                                >
                                  <IconEdit size={16} />
                                </Button>
                                <ActionIcon
                                  color="red"
                                  variant="light"
                                  onClick={() => handleDeleteModule(module.id)}
                                >
                                  <IconTrash size={16} />
                                </ActionIcon>
                              </Group>
                            </Table.Td>
                          </Table.Tr>
                        ))}
                      </Table.Tbody>
                    </Table>
                  </Accordion.Panel>
                </Accordion.Item>
              ))}
            </Accordion>
          )}
        </Paper>

        {/* Кнопка возврата */}
        <Group justify="center" mt="xl">
          <Button
            component={Link}
            to="/"
            variant="outline"
          >
            Вернуться к списку курсов
          </Button>
        </Group>
      </Container>
    </Layout>
  );
}