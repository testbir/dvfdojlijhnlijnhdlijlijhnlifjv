// admin-frontend/src/pages/ModuleCreatePage.tsx

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import {
  Container,
  Title,
  TextInput,
  Button,
  NumberInput,
  Notification,
  Select,
  Group,
  Paper,
  Text,
  Stack,
  Alert,
  Badge,
} from '@mantine/core';
import { IconCoins, IconFolder } from '@tabler/icons-react';
import { modulesApi } from '../services/adminApi';

export default function ModuleCreatePage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [groupTitle, setGroupTitle] = useState('');
  const [order, setOrder] = useState<number>(1);
  const [spAward, setSpAward] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [existingGroups, setExistingGroups] = useState<string[]>([]);

  useEffect(() => {
    fetchExistingGroups();
  }, [courseId]);

  const fetchExistingGroups = async () => {
    if (!courseId) return;
    
    try {
      const modules = await modulesApi.getCourseModules(Number(courseId));
      const groups = new Set<string>();
      
      modules.forEach((module: any) => {
        if (module.group_title) {
          groups.add(module.group_title);
        }
      });
      
      setExistingGroups(Array.from(groups));
      
      // Устанавливаем порядок для нового модуля
      if (modules.length > 0) {
        const maxOrder = Math.max(...modules.map((m: any) => m.order || 0));
        setOrder(maxOrder + 1);
      }
    } catch (err) {
      console.error('Ошибка при загрузке групп:', err);
    }
  };

  const handleSubmit = async () => {
    if (!title.trim()) {
      setError('Введите название модуля');
      return;
    }

    if (!courseId) {
      setError('ID курса не определен');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      await modulesApi.createModule(Number(courseId), {
        title,
        group_title: groupTitle || undefined,
        order,
        sp_award: spAward
      });
      
      navigate(`/courses/${courseId}/structure`);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Ошибка при создании модуля');
    } finally {
      setLoading(false);
    }
  };

  const groupOptions = [
    { value: '', label: 'Без группы' },
    ...existingGroups.map(g => ({ value: g, label: g })),
    { value: 'new', label: '+ Создать новую группу' }
  ];

  const [showNewGroupInput, setShowNewGroupInput] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');

  const handleGroupChange = (value: string | null) => {
    if (value === 'new') {
      setShowNewGroupInput(true);
      setGroupTitle('');
    } else {
      setShowNewGroupInput(false);
      setGroupTitle(value || '');
      setNewGroupName('');
    }
  };

  const handleNewGroupConfirm = () => {
    if (newGroupName.trim()) {
      setGroupTitle(newGroupName.trim());
      setShowNewGroupInput(false);
    }
  };

  return (
    <Layout>
      <Container size="md">
        <Title order={2} ta="center" mb="xl">
          Создание модуля
        </Title>

        {error && (
          <Notification color="red" onClose={() => setError(null)} mb="md">
            {error}
          </Notification>
        )}

        <Stack gap="lg">
          {/* Основная информация */}
          <Paper shadow="sm" p="md" withBorder>
            <Stack gap="md">
              <TextInput
                label="Название модуля"
                value={title}
                onChange={(e) => setTitle(e.currentTarget.value)}
                placeholder="Введите название модуля"
                required
                error={!title.trim() && 'Обязательное поле'}
              />

              {!showNewGroupInput ? (
                <Select
                  label="Группа модулей"
                  value={groupTitle}
                  onChange={handleGroupChange}
                  data={groupOptions}
                  placeholder="Выберите группу или создайте новую"
                  leftSection={<IconFolder size={16} />}
                  clearable
                />
              ) : (
                <div>
                  <TextInput
                    label="Название новой группы"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.currentTarget.value)}
                    placeholder="Введите название группы"
                    rightSection={
                      <Group gap="xs">
                        <Button size="xs" onClick={handleNewGroupConfirm}>
                          OK
                        </Button>
                        <Button 
                          size="xs" 
                          variant="outline" 
                          onClick={() => {
                            setShowNewGroupInput(false);
                            setNewGroupName('');
                          }}
                        >
                          Отмена
                        </Button>
                      </Group>
                    }
                  />
                </div>
              )}

              {groupTitle && (
                <Alert color="blue" variant="light">
                  Модуль будет добавлен в группу: <strong>{groupTitle}</strong>
                </Alert>
              )}
            </Stack>
          </Paper>

          {/* Настройки модуля */}
          <Paper shadow="sm" p="md" withBorder>
            <Stack gap="md">
              <Text fw={500} size="lg" mb="xs">Настройки модуля</Text>
              
              <NumberInput
                label="Порядок отображения"
                value={order}
                onChange={(val) => setOrder(typeof val === 'number' ? val : 1)}
                min={1}
                placeholder="1"
                description="Чем меньше число, тем выше модуль в списке"
              />

              <NumberInput
                label="SP баллы за прохождение"
                value={spAward}
                onChange={(val) => setSpAward(typeof val === 'number' ? val : 0)}
                min={0}
                max={1000}
                placeholder="0"
                leftSection={<IconCoins size={16} />}
                description="Количество баллов, которое получит ученик после завершения модуля"
              />

              {spAward > 0 && (
                <Alert color="green" variant="light">
                  Ученик получит <Badge color="green" size="lg">{spAward} SP</Badge> после завершения этого модуля
                </Alert>
              )}
            </Stack>
          </Paper>

          {/* Кнопки действий */}
          <Group justify="space-between" mt="xl">
            <Button
              variant="outline"
              onClick={() => navigate(`/courses/${courseId}/structure`)}
            >
              Отмена
            </Button>
            <Button 
              onClick={handleSubmit}
              loading={loading}
              disabled={!title.trim()}
            >
              Создать модуль
            </Button>
          </Group>
        </Stack>
      </Container>
    </Layout>
  );
}