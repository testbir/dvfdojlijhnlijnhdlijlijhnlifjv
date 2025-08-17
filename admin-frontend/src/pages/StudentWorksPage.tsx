// admin-frontend/src/pages/StudentWorksPage.tsx

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
  Card,
  Grid,
} from '@mantine/core';
import { 
  IconTrash, 
  IconArrowUp, 
  IconArrowDown, 
  IconPlus,
  IconUpload,
  IconBrandTelegram 
} from '@tabler/icons-react';
import Layout from '../components/Layout';
import { studentWorksApi, uploadApi } from '../services/adminApi';

interface StudentWork {
  image: string;
  description: string;
  bot_tag?: string;
  order: number;
}

export default function StudentWorksPage() {
  const { courseId: courseIdParam } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const cid = Number(courseIdParam);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [title, setTitle] = useState('Работы наших учеников');
  const [description, setDescription] = useState('');
  const [works, setWorks] = useState<StudentWork[]>([]);
  const [hasExisting, setHasExisting] = useState(false);

 useEffect(() => {
   if (!Number.isInteger(cid) || cid <= 0) {
     setError('Некорректный идентификатор курса');
     setLoading(false);
     return;
   }
   fetchData(cid);
 }, [cid]);

  const fetchData = async (id: number) => {
    
    try {
      setLoading(true);
      const data = await studentWorksApi.getWorks(id);
      
      if (data) {
        setTitle(data.title || 'Работы наших учеников');
        setDescription(data.description || '');
        setWorks(data.works?.sort((a: any, b: any) => a.order - b.order) || []);
        setHasExisting(true);
      }
    } catch (err: any) {
      if (err.response?.status !== 404) {
        setError('Ошибка при загрузке данных');
        console.error(err);
      }
    } finally {
      setLoading(false);
    }
  };

  const addWork = () => {
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
    (newWorks[index] as any)[field] = value;
    setWorks(newWorks);
  };

  const deleteWork = (index: number) => {
    if (window.confirm('Удалить эту работу?')) {
      setWorks(works.filter((_, i) => i !== index));
    }
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
    [newWorks[index], newWorks[targetIndex]] = [newWorks[targetIndex], newWorks[index]];
    
    // Обновляем order
    newWorks.forEach((work, i) => {
      work.order = i;
    });
    
    setWorks(newWorks);
  };

  const handleImageUpload = async (index: number, file: File | null) => {
    if (!file) return;

    try {
      setUploading(true);
      const result = await uploadApi.uploadImage(file, 'student-works');
      updateWork(index, 'image', result.url);
      setSuccess('Изображение загружено');
    } catch (err) {
      setError('Ошибка при загрузке изображения');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

   const handleSave = async () => {
     if (!Number.isInteger(cid) || cid <= 0) return;

    if (!title.trim()) {
      setError('Введите заголовок');
      return;
    }

    if (works.length === 0) {
      setError('Добавьте хотя бы одну работу');
      return;
    }

    // Проверяем, что все работы имеют изображения
    const invalidWorks = works.filter(w => !w.image);
    if (invalidWorks.length > 0) {
      setError('Загрузите изображения для всех работ');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const data = {
        title,
        description,
        works: works.map((w, i) => ({ ...w, order: i }))
      };

      if (hasExisting) { 
        await studentWorksApi.updateWorks(cid, data); 
      } else { 
        await studentWorksApi.createWorks(cid, data); 
        setHasExisting(true);
      }

      setSuccess('Работы учеников сохранены');
      setTimeout(() => {
        navigate(`/courses/${cid}/structure`);
      }, 1500);
    } catch (err) {
      setError('Ошибка при сохранении');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

 const handleDelete = async () => {
   if (!Number.isInteger(cid) || cid <= 0 || !hasExisting) return;
    
    if (!window.confirm('Удалить секцию работ учеников? Это действие необратимо.')) {
      return;
    }

    try {
      setSaving(true);
      await studentWorksApi.deleteWorks(cid);
      setSuccess('Секция работ удалена');
      setTimeout(() => {
        navigate(`/courses/${cid}/structure`);
      }, 1500);
    } catch (err) {
      setError('Ошибка при удалении');
      console.error(err);
    } finally {
      setSaving(false);
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
        <Group justify="space-between" mb="xl">
          <Title order={2}>Работы учеников</Title>
          {hasExisting && (
            <Button color="red" variant="outline" onClick={handleDelete}>
              Удалить секцию
            </Button>
          )}
        </Group>

        {error && (
          <Notification color="red" onClose={() => setError(null)} mb="md">
            {error}
          </Notification>
        )}

        {success && (
          <Notification color="green" onClose={() => setSuccess(null)} mb="md">
            {success}
          </Notification>
        )}

        <Stack gap="lg">
          <TextInput
            label="Заголовок секции"
            value={title}
            onChange={(e) => setTitle(e.currentTarget.value)}
            placeholder="Работы наших учеников"
            required
          />

          <Textarea
            label="Описание"
            value={description}
            onChange={(e) => setDescription(e.currentTarget.value)}
            placeholder="Посмотрите, какие проекты создают наши ученики"
            minRows={2}
          />

          <Paper p="md" withBorder>
            <Group justify="space-between" mb="md">
              <Text fw={500}>Работы учеников</Text>
              <Button
                leftSection={<IconPlus size={16} />}
                onClick={addWork}
                variant="light"
              >
                Добавить работу
              </Button>
            </Group>

            {works.length === 0 ? (
              <Alert color="blue">
                Нажмите "Добавить работу", чтобы начать добавлять примеры работ учеников
              </Alert>
            ) : (
              <Stack gap="md">
                {works.map((work, index) => (
                  <Card key={index} shadow="sm" padding="lg" withBorder>
                    <Grid>
                      <Grid.Col span={{ base: 12, md: 4 }}>
                        {work.image ? (
                          <div>
                            <Image
                              src={work.image}
                              height={150}
                              alt={`Работа ${index + 1}`}
                              radius="md"
                              mb="xs"
                            />
                            <FileInput
                              accept="image/*"
                              onChange={(file) => handleImageUpload(index, file)}
                              placeholder="Изменить изображение"
                              leftSection={<IconUpload size={14} />}
                              size="xs"
                              disabled={uploading}
                            />
                          </div>
                        ) : (
                          <FileInput
                            accept="image/*"
                            onChange={(file) => handleImageUpload(index, file)}
                            placeholder="Загрузить изображение"
                            leftSection={<IconUpload size={14} />}
                            required
                            disabled={uploading}
                          />
                        )}
                      </Grid.Col>

                      <Grid.Col span={{ base: 12, md: 8 }}>
                        <Stack gap="sm">
                          <Textarea
                            placeholder="Описание работы"
                            value={work.description}
                            onChange={(e) => updateWork(index, 'description', e.currentTarget.value)}
                            minRows={2}
                          />

                          <TextInput
                            placeholder="@telegram_bot (опционально)"
                            value={work.bot_tag || ''}
                            onChange={(e) => updateWork(index, 'bot_tag', e.currentTarget.value)}
                            leftSection={<IconBrandTelegram size={16} />}
                          />

                          <Group justify="space-between">
                            <Badge>Позиция: {index + 1}</Badge>
                            <Group gap="xs">
                              <ActionIcon
                                onClick={() => moveWork(index, 'up')}
                                disabled={index === 0}
                                variant="light"
                              >
                                <IconArrowUp size={16} />
                              </ActionIcon>
                              <ActionIcon
                                onClick={() => moveWork(index, 'down')}
                                disabled={index === works.length - 1}
                                variant="light"
                              >
                                <IconArrowDown size={16} />
                              </ActionIcon>
                              <ActionIcon
                                onClick={() => deleteWork(index)}
                                color="red"
                                variant="light"
                              >
                                <IconTrash size={16} />
                              </ActionIcon>
                            </Group>
                          </Group>
                        </Stack>
                      </Grid.Col>
                    </Grid>
                  </Card>
                ))}
              </Stack>
            )}
          </Paper>

          <Group justify="space-between" mt="xl">
            <Button
              variant="outline"
              onClick={() => navigate(`/courses/${cid}/structure`)}
            >
              Отмена
            </Button>
            <Button
              onClick={handleSave}
              loading={saving}
              disabled={uploading}
            >
              {hasExisting ? 'Сохранить изменения' : 'Создать секцию'}
            </Button>
          </Group>
        </Stack>
      </Container>
    </Layout>
  );
}