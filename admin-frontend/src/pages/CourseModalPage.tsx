// src/pages/CourseModalPage.tsx

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Title,
  TextInput,
  Button,
  Group,
  Stack,
  Paper,
  ActionIcon,
  Notification,
  Textarea,
  Loader,
  Center,
  Alert,
  FileInput,
  Image,
  Text,
  Badge,
} from '@mantine/core';
import { IconTrash, IconArrowUp, IconArrowDown, IconPlus } from '@tabler/icons-react';
import Layout from '../components/Layout';
import axios from '../api/axiosInstance';



interface ModalBlock {
  type: 'text' | 'image';
  content: string;
  order: number;
}

export default function CourseModalPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [title, setTitle] = useState('');
  const [blocks, setBlocks] = useState<ModalBlock[]>([]);
  const [hasExistingModal, setHasExistingModal] = useState(false);

  useEffect(() => {
    fetchModalData();
  }, [courseId]);

  const fetchModalData = async () => {
    try {
      const res = await axios.get(`/admin/course-extras/modal/${courseId}/`);
      if (res.data) {
        setTitle(res.data.title);
        setBlocks(res.data.blocks.sort((a: any, b: any) => a.order - b.order));
        setHasExistingModal(true);
      }
    } catch (err) {
      console.error('Ошибка загрузки модального окна:', err);
    } finally {
      setLoading(false);
    }
  };

  const addBlock = (type: 'text' | 'image') => {
    const maxOrder = blocks.length > 0 ? Math.max(...blocks.map(b => b.order)) : -1;
    setBlocks([...blocks, { type, content: '', order: maxOrder + 1 }]);
  };

  const updateBlock = (index: number, content: string) => {
    const newBlocks = [...blocks];
    newBlocks[index].content = content;
    setBlocks(newBlocks);
  };

  const deleteBlock = (index: number) => {
    setBlocks(blocks.filter((_, i) => i !== index));
  };

  const moveBlock = (index: number, direction: 'up' | 'down') => {
    if (
      (direction === 'up' && index === 0) ||
      (direction === 'down' && index === blocks.length - 1)
    ) {
      return;
    }

    const newBlocks = [...blocks];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    
    // Меняем местами order
    const tempOrder = newBlocks[index].order;
    newBlocks[index].order = newBlocks[targetIndex].order;
    newBlocks[targetIndex].order = tempOrder;
    
    // Меняем местами элементы
    [newBlocks[index], newBlocks[targetIndex]] = [newBlocks[targetIndex], newBlocks[index]];
    
    setBlocks(newBlocks);
  };

  const handleImageUpload = async (file: File, blockIndex: number) => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      const res = await axios.post('/admin/upload/content', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      updateBlock(blockIndex, res.data.url);
    } catch (err) {
      setError('Ошибка при загрузке изображения');
    } finally {
      setUploading(false);
    }
  };

  const handleSave = async () => {
    if (!title.trim()) {
      setError('Введите заголовок модального окна');
      return;
    }

    // Проверяем, что все блоки заполнены
    const emptyBlocks = blocks.filter(b => !b.content.trim());
    if (emptyBlocks.length > 0) {
      setError('Заполните все блоки или удалите пустые');
      return;
    }

    setSaving(true);
    try {
      const blocksData = blocks.map((block, index) => ({
        type: block.type,
        content: block.content,
        order: index
      }));

      if (hasExistingModal) {
        await axios.put(`/admin/course-extras/modal/${courseId}/`, {
          title,
          blocks: blocksData
        });
      } else {
        await axios.post(`/admin/course-extras/modal/${courseId}/`, {
          title,
          blocks: blocksData
        });
      }
      
      navigate(`/courses/${courseId}/structure`);
    } catch (err) {
      console.error('Ошибка сохранения:', err);
      setError('Ошибка при сохранении модального окна');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Вы уверены, что хотите удалить модальное окно?')) return;
    
    try {
      await axios.delete(`/admin/course-extras/modal/${courseId}/`);
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
      <Container size="md">
        <Title order={2} ta="center" mb="lg">
          {hasExistingModal ? 'Редактирование' : 'Создание'} модального окна курса
        </Title>

        {error && (
          <Notification color="red" mb="lg" onClose={() => setError(null)}>
            {error}
          </Notification>
        )}

        <Alert color="blue" mb="lg">
          Модальное окно будет показано пользователям при открытии страницы курса.
          Вы можете добавлять текстовые блоки и изображения в любом порядке.
        </Alert>

        <TextInput
          label="Заголовок модального окна"
          value={title}
          onChange={(e) => setTitle(e.currentTarget.value)}
          placeholder="Например: Важная информация о курсе"
          required
          mb="xl"
        />

        <Stack gap="md">
          <Group justify="space-between" mb="sm">
            <Title order={4}>Блоки контента</Title>
            <Group>
              <Button
                leftSection={<IconPlus size={16} />}
                onClick={() => addBlock('text')}
                variant="light"
              >
                Добавить текст
              </Button>
              <Button
                leftSection={<IconPlus size={16} />}
                onClick={() => addBlock('image')}
                variant="light"
                color="green"
              >
                Добавить изображение
              </Button>
            </Group>
          </Group>

          {blocks.length === 0 && (
            <Paper p="xl" withBorder style={{ borderStyle: 'dashed' }}>
              <Text ta="center" c="dimmed">
                Нажмите кнопки выше, чтобы добавить контент в модальное окно
              </Text>
            </Paper>
          )}

          {blocks.map((block, index) => (
            <Paper key={index} p="md" withBorder>
              <Group justify="space-between" mb="sm">
                <Badge color={block.type === 'text' ? 'blue' : 'green'}>
                  {block.type === 'text' ? 'Текст' : 'Изображение'}
                </Badge>
                <Group gap="xs">
                  <ActionIcon
                    variant="light"
                    onClick={() => moveBlock(index, 'up')}
                    disabled={index === 0}
                  >
                    <IconArrowUp size={16} />
                  </ActionIcon>
                  <ActionIcon
                    variant="light"
                    onClick={() => moveBlock(index, 'down')}
                    disabled={index === blocks.length - 1}
                  >
                    <IconArrowDown size={16} />
                  </ActionIcon>
                  <ActionIcon
                    color="red"
                    variant="light"
                    onClick={() => deleteBlock(index)}
                  >
                    <IconTrash size={16} />
                  </ActionIcon>
                </Group>
              </Group>

              {block.type === 'text' ? (
              <Textarea
                value={block.content}
                onChange={(e) => updateBlock(index, e.currentTarget.value)}
                placeholder="Вставьте HTML (p, ul, strong и т.д.)"
                autosize
                minRows={8}
              />

              ) : (
                <>
                  <FileInput
                    accept="image/*"
                    onChange={(file) => file && handleImageUpload(file, index)}
                    placeholder="Загрузить изображение"
                    disabled={uploading}
                    mb="sm"
                  />
                  {block.content && (
                    <>
                      <Image src={block.content} height={200} radius="sm" mb="sm" />
                      <TextInput
                        value={block.content}
                        onChange={(e) => updateBlock(index, e.currentTarget.value)}
                        placeholder="URL изображения"
                        size="xs"
                      />
                    </>
                  )}
                </>
              )}
            </Paper>
          ))}
        </Stack>

        <Group justify="space-between" mt="xl">
          <Button variant="light" onClick={() => navigate(-1)}>
            Отмена
          </Button>
          <Group>
            {hasExistingModal && (
              <Button color="red" variant="light" onClick={handleDelete}>
                Удалить модальное окно
              </Button>
            )}
            <Button
              onClick={handleSave}
              loading={saving}
              disabled={!title.trim() || blocks.length === 0}
            >
              {hasExistingModal ? 'Сохранить изменения' : 'Создать модальное окно'}
            </Button>
          </Group>
        </Group>
      </Container>
    </Layout>
  );
}