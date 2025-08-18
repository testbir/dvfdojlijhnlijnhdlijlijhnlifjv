// admin-frontend/src/pages/StatisticsPage.tsx

import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import type { PieLabelRenderProps } from 'recharts/types/polar/Pie';
import {
  Container,
  Title,
  Card,
  Grid,
  Text,
  Group,
  Progress,
  Table,
  Badge,
  Loader,
  Paper,
} from '@mantine/core';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { statisticsApi } from '../services/adminApi';

interface Statistics {
  total_users: number;
  active_users: number;
  total_courses: number;
  free_courses: number;
  paid_courses: number;
  total_revenue: number;
  registrations_last_30_days: number;
  popular_courses: PopularCourse[];
  user_activity: UserActivity[];
  revenue_by_month: RevenueData[];
}

interface PopularCourse {
  id: number;
  title: string;
  enrollments: number;
  completion_rate: number;
}

interface UserActivity {
  date: string;
  registrations: number;
  active_users: number;
}

interface RevenueData {
  month: string;
  revenue: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function StatisticsPage() {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      const data = await statisticsApi.getPlatformStats();
      setStats(data);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return (
      <Layout>
        <Container>
          <Loader />
        </Container>
      </Layout>
    );
  }

  const courseTypeData = [
    { name: 'Бесплатные', value: stats.free_courses },
    { name: 'Платные', value: stats.paid_courses },
  ];

  return (
    <Layout>
      <Container size="xl">
        <Title order={2} ta="center" mb="lg">
          Статистика платформы
        </Title>

        {/* Основные метрики */}
        <Grid mb="xl">
          <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
            <Card shadow="sm" radius="md">
              <Text size="sm" c="dimmed">Всего пользователей</Text>
              <Title order={2}>{stats.total_users}</Title>
              <Progress value={(stats.active_users / stats.total_users) * 100} mt="sm" />
              <Text size="xs" c="dimmed" mt="xs">
                {stats.active_users} активных
              </Text>
            </Card>
          </Grid.Col>

          <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
            <Card shadow="sm" radius="md">
              <Text size="sm" c="dimmed">Всего курсов</Text>
              <Title order={2}>{stats.total_courses}</Title>
              <Group mt="sm">
                <Badge color="green">{stats.free_courses} бесплатных</Badge>
                <Badge color="blue">{stats.paid_courses} платных</Badge>
              </Group>
            </Card>
          </Grid.Col>

          <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
            <Card shadow="sm" radius="md">
              <Text size="sm" c="dimmed">Общая выручка</Text>
              <Title order={2}>{stats.total_revenue.toLocaleString()} ₽</Title>
              <Text size="xs" c="green" mt="sm">
                +15% за месяц
              </Text>
            </Card>
          </Grid.Col>

          <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
            <Card shadow="sm" radius="md">
              <Text size="sm" c="dimmed">Новых за 30 дней</Text>
              <Title order={2}>{stats.registrations_last_30_days}</Title>
              <Text size="xs" c="dimmed" mt="sm">
                пользователей
              </Text>
            </Card>
          </Grid.Col>
        </Grid>

        {/* Графики */}
        <Grid mb="xl">
          <Grid.Col span={{ base: 12, md: 8 }}>
            <Paper shadow="sm" radius="md" p="md">
              <Title order={4} mb="md">Активность пользователей</Title>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats.user_activity}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="registrations" stroke="#8884d8" name="Регистрации" />
                  <Line type="monotone" dataKey="active_users" stroke="#82ca9d" name="Активные" />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 4 }}>
            <Paper shadow="sm" radius="md" p="md">
              <Title order={4} mb="md">Типы курсов</Title>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={courseTypeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry: PieLabelRenderProps) => {
                      const { name, value } = entry;
                      return `${name}: ${value}`;
                    }}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {courseTypeData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                        name={entry.name}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid.Col>
        </Grid>

        {/* Выручка по месяцам */}
        <Paper shadow="sm" radius="md" p="md" mb="xl">
          <Title order={4} mb="md">Выручка по месяцам</Title>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.revenue_by_month}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `${value} ₽`} />
              <Bar dataKey="revenue" fill="#8884d8" name="Выручка" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>

        {/* Популярные курсы */}
        <Paper shadow="sm" radius="md" p="md">
          <Title order={4} mb="md">Популярные курсы</Title>
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Курс</Table.Th>
                <Table.Th>Записей</Table.Th>
                <Table.Th>Процент завершения</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {stats.popular_courses.map((course) => (
                <Table.Tr key={course.id}>
                  <Table.Td>{course.title}</Table.Td>
                  <Table.Td>{course.enrollments}</Table.Td>
                  <Table.Td>
                    <Group>
                      <Progress value={course.completion_rate} style={{ flex: 1 }} />
                      <Text size="sm">{course.completion_rate}%</Text>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Paper>
      </Container>
    </Layout>
  );
}
