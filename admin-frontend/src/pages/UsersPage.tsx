// src/pages/UsersPage.tsx

import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import {
  Container,
  Title,
  Table,
  Button,
  Group,
  Badge,
  TextInput,
  Modal,
  Switch,
  Loader,
  ActionIcon,
  Center,
  Stack,
  Text,
  ScrollArea,
} from '@mantine/core';
import { IconSearch, IconEdit } from '@tabler/icons-react';
import axios from '../api/axiosInstance';

interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_email_confirmed: boolean;
  courses_purchased: number;
  last_login?: string;
}

interface CourseAccess {
  course_id: number;
  course_title: string;
  purchased_at: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userCourses, setUserCourses] = useState<CourseAccess[]>([]);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await axios.get('/admin/users/');
      setUsers(res.data.users);
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserCourses = async (userId: number) => {
    try {
      const res = await axios.get(`/admin/users/${userId}/courses/`);
      setUserCourses(res.data.courses);
    } catch (error) {
      console.error('Ошибка загрузки курсов пользователя:', error);
    }
  };

  const handleViewUser = async (user: User) => {
    setSelectedUser(user);
    await fetchUserCourses(user.id);
    setModalOpen(true);
  };

  const handleToggleActive = async (userId: number, currentStatus: boolean) => {
    try {
      await axios.patch(`/admin/users/${userId}/toggle-active/`, {
        is_active: !currentStatus
      });
      setUsers(users.map(u => 
        u.id === userId ? { ...u, is_active: !currentStatus } : u
      ));
    } catch (error) {
      console.error('Ошибка изменения статуса:', error);
    }
  };

  const handleGrantAccess = async (userId: number, courseId: number) => {
    try {
      await axios.post(`/admin/users/${userId}/grant-access/`, { course_id: courseId });
      alert('Доступ предоставлен!');
      // Обновляем список курсов пользователя
      await fetchUserCourses(userId);
    } catch (error) {
      console.error('Ошибка предоставления доступа:', error);
      alert('Ошибка при предоставлении доступа');
    }
  };

  const filteredUsers = users.filter(user =>
    user.email.toLowerCase().includes(search.toLowerCase()) ||
    user.username.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <Layout>
        <Container fluid px="xl">
          <Center h={400}>
            <Loader size="lg" />
          </Center>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container fluid px="xl">
        <Title order={2} ta="center" mb="lg">
          Управление пользователями
        </Title>

        <TextInput
          placeholder="Поиск по email или username..."
          leftSection={<IconSearch size={16} />}
          value={search}
          onChange={(e) => setSearch(e.currentTarget.value)}
          mb="md"
          maw={400}
        />

        <ScrollArea>
          <Table withRowBorders withColumnBorders highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>ID</Table.Th>
                <Table.Th>Email</Table.Th>
                <Table.Th>Username</Table.Th>
                <Table.Th>Статус</Table.Th>
                <Table.Th>Email подтвержден</Table.Th>
                <Table.Th>Курсов куплено</Table.Th>
                <Table.Th>Действия</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {filteredUsers.map((user) => (
                <Table.Tr key={user.id}>
                  <Table.Td>{user.id}</Table.Td>
                  <Table.Td>{user.email}</Table.Td>
                  <Table.Td>{user.username}</Table.Td>
                  <Table.Td>
                    <Switch
                      checked={user.is_active}
                      onChange={() => handleToggleActive(user.id, user.is_active)}
                      label={user.is_active ? 'Активен' : 'Заблокирован'}
                      color={user.is_active ? 'green' : 'red'}
                    />
                  </Table.Td>
                  <Table.Td>
                    <Badge color={user.is_email_confirmed ? 'green' : 'red'}>
                      {user.is_email_confirmed ? 'Да' : 'Нет'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text ta="center">{user.courses_purchased}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      <ActionIcon
                        variant="light"
                        onClick={() => handleViewUser(user)}
                        title="Просмотр детальной информации"
                      >
                        <IconEdit size={16} />
                      </ActionIcon>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </ScrollArea>

        <Modal
          opened={modalOpen}
          onClose={() => setModalOpen(false)}
          title={`Пользователь: ${selectedUser?.email}`}
          size="lg"
        >
          {selectedUser && (
            <Stack>
              <Group>
                <Text fw={500}>ID:</Text>
                <Text>{selectedUser.id}</Text>
              </Group>
              
              <Group>
                <Text fw={500}>Username:</Text>
                <Text>{selectedUser.username}</Text>
              </Group>

              <Group>
                <Text fw={500}>Статус:</Text>
                <Badge color={selectedUser.is_active ? 'green' : 'red'}>
                  {selectedUser.is_active ? 'Активен' : 'Заблокирован'}
                </Badge>
              </Group>

              <Title order={4} mt="md" mb="sm">Доступ к курсам:</Title>
              
              {userCourses.length > 0 ? (
                <ScrollArea h={200}>
                  <Table>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Курс</Table.Th>
                        <Table.Th>Дата покупки</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {userCourses.map((course) => (
                        <Table.Tr key={course.course_id}>
                          <Table.Td>{course.course_title}</Table.Td>
                          <Table.Td>
                            {new Date(course.purchased_at).toLocaleDateString()}
                          </Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                </ScrollArea>
              ) : (
                <Text c="dimmed" ta="center" py="md">
                  Нет купленных курсов
                </Text>
              )}

              <Button
                mt="md"
                fullWidth
                onClick={() => {
                  const courseId = prompt('Введите ID курса для предоставления доступа:');
                  if (courseId && !isNaN(parseInt(courseId))) {
                    handleGrantAccess(selectedUser.id, parseInt(courseId));
                  }
                }}
              >
                Предоставить доступ к курсу
              </Button>
            </Stack>
          )}
        </Modal>
      </Container>
    </Layout>
  );
}