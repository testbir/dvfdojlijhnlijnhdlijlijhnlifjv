// src/pages/StudentWorksPage.tsx

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Title,
  TextInput,
  Textarea,
  Button,
  Group,
  Stack,
  Paper,
  ActionIcon,
  Notification,
  Loader,
  Center,
  Alert,
  FileInput,
  Image,
  Text,
  Badge,
  Grid,
} from '@mantine/core';
import { IconTrash, IconArrowUp, IconArrowDown, IconPlus } from '@tabler/icons-react';
import Layout from '../components/Layout';
import axios from '../api/axiosInstance';

interface StudentWork {
  image: string;
  description: string;
  bot_tag: string;
  order: number;
}

export default function StudentWorksPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [title, setTitle] = useState('Работы учеников нашего курса');
  const [description, setDescription] = useState('');
  const [works, setWorks] = useState<StudentWork[]>([]);
  const [hasExistingSection, setHasExistingSection] = useState(false);

  useEffect(() => {
    fetchStudentWorks();
  }, [courseId]);

  const fetchStudentWorks = async () => {
    try {
      const res = await axios.get(`/admin/course-extras/student-works/${courseId}/`);
      if (res.data) {
        setTitle(res.data.title);
        setDescription(res.data.description);
        setWorks(res.data.works.sort((a: any, b: any) => a.order - b.order));
        setHasExistingSection(true);
      }
    } catch (err) {
      console.error('Ошибка загрузки работ учеников:', err);
    } finally {
      setLoading(false);
    }
  };

  const addWork = () => {
    if (works.length >= 4) {
      setError('Можно добавить максимум 4 работы');
      return;
    }
    const maxOrder = works.length > 0 ? Math.max(...works.map(w => w.order)) : -1;
    setWorks([...works, { 
      image: '', 
      description: '', 
      bot_tag: '', 
      order: maxOrder + 1 
    }]);
  };

  const updateWork = (index: number, field: keyof StudentWork, value: string) => {
    const newWorks = [...works];
    newWorks[index] = { ...newWorks[index], [field]: value };
    setWorks(newWorks);
  };

  const deleteWork = (index: number) => {
    setWorks(works.filter((_, i) => i !== index));
  };

  const moveWork = (index: number, direction: 'up' | 'down') => {
    if (
      (direction === 'up' && index === 0) ||
      (direction === 'down' && index === works.length - 1)
    ) {
      return;
    }

    const newWorks = [...works];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    
    // Меняем местами order
    const tempOrder = newWorks[index].order;
    newWorks[index].order = newWorks[targetIndex].order;
    newWorks[targetIndex].order = tempOrder;
    
    // Меняем местами элементы
    [newWorks[index], newWorks[targetIndex]] = [newWorks[targetIndex], newWorks[index]];
    
    setWorks(newWorks);
  };

  const handleImageUpload = async (file: File, workIndex: number) => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      const res = await axios.post('/admin/upload/content', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      updateWork(workIndex, 'image', res.data.url);
    } catch (err) {
      setError('Ошибка при загрузке изображения');
    } finally {
      setUploading(false);
    }
  };

  const handleSave = async () => {
    if (!title.trim() || !description.trim()) {
      setError('Заполните название и описание секции');
      return;
    }

    // Проверяем, что все работы заполнены
    const incompleteWorks = works.filter(w => !w.image.trim());
    if (incompleteWorks.length > 0) {
      setError('Загрузите изображения для всех работ или удалите пустые');
      return;
    }

    setSaving(true);
    try {
      const worksData = works.map((work, index) => ({
        image: work.image,
        description: work.description || '',
        bot_tag: work.bot_tag || '',
        order: index
      }));

      if (hasExistingSection) {
        await axios.put(`/admin/course-extras/student-works/${courseId}/`, {
          title,
          description,
          works: worksData
        });
      } else {
        await axios.post(`/admin/course-extras/student-works/${courseId}/`, {
          title,
          description,
          works: worksData
        });
      }
      
      navigate(`/courses/${courseId}/structure`);
    } catch (err) {
      console.error('Ошибка сохранения:', err);
      setError('Ошибка при сохранении работ учеников');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Вы уверены, что хотите удалить секцию работ учеников?')) return;
    
    try {
      await axios.delete(`/admin/course-extras/student-works/${courseId}/`);
      navigate(`/courses/${courseId}/structure`);
    } catch (err) {
      setError('Ошибка при удалении');
    }
  };

  if (loading) {
    return (
      <Layout>
        <Center h={400}>
          <Loader size="lg" />
        </Center>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container size="lg">
        <Title order={2} ta="center" mb="lg">
          {hasExistingSection ? 'Редактирование' : 'Создание'} секции работ учеников
        </Title>

        {error && (
          <Notification color="red" mb="lg" onClose={() => setError(null)}>
            {error}
          </Notification>
        )}

        <Alert color="blue" mb="lg">
          Добавьте примеры работ учеников вашего курса. Можно добавить до 4 работ с описанием и тегом бота.
        </Alert>

        <Stack gap="md" mb="xl">
          <TextInput
            label="Название секции"
            value={title}
            onChange={(e) => setTitle(e.currentTarget.value)}
            placeholder="Например: Работы учеников нашего курса"
            required
          />

          <Textarea
            label="Описание секции"
            value={description}
            onChange={(e) => setDescription(e.currentTarget.value)}
            placeholder="Например: Уже в процессе обучения наши студенты создают настоящие Telegram-боты..."
            required
            minRows={2}
            autosize
          />
        </Stack>

        <Stack gap="md">
          <Group justify="space-between" mb="sm">
            <Title order={4}>Примеры работ</Title>
            <Button
              leftSection={<IconPlus size={16} />}
              onClick={addWork}
              variant="light"
              disabled={works.length >= 4}
            >
              Добавить работу
            </Button>
          </Group>

          {works.length === 0 && (
            <Paper p="xl" withBorder style={{ borderStyle: 'dashed' }}>
              <Text ta="center" c="dimmed">
                Нажмите кнопку выше, чтобы добавить примеры работ учеников
              </Text>
            </Paper>
          )}

          <Grid>
            {works.map((work, index) => (
              <Grid.Col key={index} span={{ base: 12, md: 6 }}>
                <Paper p="md" withBorder h="100%">
                  <Group justify="space-between" mb="sm">
                    <Badge>Работа #{index + 1}</Badge>
                    <Group gap="xs">
                      <ActionIcon
                        variant="light"
                        onClick={() => moveWork(index, 'up')}
                        disabled={index === 0}
                      >
                        <IconArrowUp size={16} />
                      </ActionIcon>
                      <ActionIcon
                        variant="light"
                        onClick={() => moveWork(index, 'down')}
                        disabled={index === works.length - 1}
                      >
                        <IconArrowDown size={16} />
                      </ActionIcon>
                      <ActionIcon
                        color="red"
                        variant="light"
                        onClick={() => deleteWork(index)}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Group>
                  </Group>

                  <Stack gap="sm">
                    <div>
                      <FileInput
                        label="Изображение работы"
                        accept="image/*"
                        onChange={(file) => file && handleImageUpload(file, index)}
                        placeholder="Загрузить скриншот"
                        disabled={uploading}
                        required
                      />
                      {work.image && (
                        <Image 
                          src={work.image} 
                          height={200} 
                          radius="sm" 
                          mt="sm"
                          fit="contain"
                        />
                      )}
                    </div>

                    <Textarea
                      label="Описание работы"
                      value={work.description}
                      onChange={(e) => updateWork(index, 'description', e.currentTarget.value)}
                      placeholder="Например: Бот для учета личных финансов"
                      minRows={2}
                      autosize
                    />

                    <TextInput
                      label="Тег бота"
                      value={work.bot_tag}
                      onChange={(e) => updateWork(index, 'bot_tag', e.currentTarget.value)}
                      placeholder="@example_bot"
                      leftSection={<Text size="sm" c="dimmed">@</Text>}
                    />
                  </Stack>
                </Paper>
              </Grid.Col>
            ))}
          </Grid>
        </Stack>

        <Group justify="space-between" mt="xl">
          <Button variant="light" onClick={() => navigate(-1)}>
            Отмена
          </Button>
          <Group>
            {hasExistingSection && (
              <Button color="red" variant="light" onClick={handleDelete}>
                Удалить секцию
              </Button>
            )}
            <Button
              onClick={handleSave}
              loading={saving}
              disabled={!title.trim() || !description.trim() || works.length === 0}
            >
              {hasExistingSection ? 'Сохранить изменения' : 'Создать секцию'}
            </Button>
          </Group>
        </Group>
      </Container>
    </Layout>
  );
}