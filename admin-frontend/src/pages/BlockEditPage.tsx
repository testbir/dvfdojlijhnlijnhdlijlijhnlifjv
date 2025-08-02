// src/pages/BlockEditPage.tsx

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../api/axiosInstance';
import Layout from '../components/Layout';
import {
  Container,
  Title,
  TextInput,
  Textarea,
  Select,
  NumberInput,
  Button,
  Loader,
  Center,
  Notification,
  FileInput,
  Image,
} from '@mantine/core';

const blockTypes = [
  { value: 'text', label: 'Текст' },
  { value: 'video', label: 'Видео' },
  { value: 'code', label: 'Код' },
  { value: 'image', label: 'Изображение' },
];

export default function BlockEditPage() {
  const { blockId } = useParams<{ blockId: string }>();
  const navigate = useNavigate();

  const [block, setBlock] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBlock = async () => {
      try {
        const res = await axios.get(`/admin/blocks/${blockId}`);
        setBlock(res.data);
      } catch {
        setError('Ошибка при загрузке блока');
      } finally {
        setLoading(false);
      }
    };
    fetchBlock();
  }, [blockId]);

  const handleFileUpload = async (file: File) => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      const res = await axios.post('/admin/upload/content', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setBlock((prev: any) => ({
        ...prev,
        content: res.data.url,
      }));
    } catch {
      setError('Ошибка при загрузке файла');
    } finally {
      setUploading(false);
    }
  };

  const handleVideoPreviewUpload = async (file: File) => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      const res = await axios.post('/admin/upload/content', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setBlock((prev: any) => ({
        ...prev,
        video_preview: res.data.url,
      }));
    } catch {
      setError('Ошибка при загрузке превью');
    } finally {
      setUploading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`/admin/blocks/${blockId}`, {
        type: block.type,
        title: block.title,
        content: block.content?.trim(),
        order: block.order,
        video_preview:
          block.type === 'video' && block.video_preview?.trim()
            ? block.video_preview.trim()
            : undefined,
      });
      navigate(-1);
    } catch {
      setError('Ошибка при сохранении');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Center>
          <Loader />
        </Center>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <Notification color="red">{error}</Notification>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container size="sm">
        <Title order={2} ta="center" mb="lg">
          Редактирование блока
        </Title>

        <Select
          label="Тип блока"
          data={blockTypes}
          value={block.type}
          onChange={(val) => setBlock({ ...block, type: val! })}
          mb="md"
        />

        <TextInput
          label="Заголовок"
          value={block.title}
          onChange={(e) => setBlock({ ...block, title: e.currentTarget.value })}
          mb="md"
        />

        {block.type === 'text' || block.type === 'code' ? (
          <Textarea
            label="Контент"
            value={block.content}
            onChange={(e) => setBlock({ ...block, content: e.currentTarget.value })}
            mb="md"
          />
        ) : (
          <>
            <FileInput
              label="Новый файл (видео/изображение)"
              onChange={(file) => file && handleFileUpload(file)}
              accept={block.type === 'image' ? 'image/*' : 'video/*'}
              mb="md"
            />
            {uploading && <Loader size="sm" mb="md" />}
            {block.type === 'image' && block.content && (
              <Image src={block.content} height={150} radius="sm" mb="md" />
            )}
            {block.type === 'video' && block.content && (
              <video src={block.content} controls style={{ width: '100%', marginBottom: 12 }} />
            )}
            <TextInput
              label="Ссылка на файл"
              value={block.content}
              onChange={(e) => setBlock({ ...block, content: e.currentTarget.value })}
              mb="md"
            />
          </>
        )}

        {block.type === 'video' && (
          <>
            <FileInput
              label="Превью к видео"
              onChange={(file) => file && handleVideoPreviewUpload(file)}
              accept="image/*"
              mb="md"
            />
            {block.video_preview && (
              <>
                <Image src={block.video_preview} height={100} radius="sm" mb="xs" />
                <TextInput
                  label="Ссылка на превью"
                  value={block.video_preview}
                  onChange={(e) =>
                    setBlock({ ...block, video_preview: e.currentTarget.value })
                  }
                  mb="md"
                />
              </>
            )}
          </>
        )}

        <NumberInput
          label="Порядок"
          value={block.order}
          onChange={(val) => setBlock({ ...block, order: val as number })}
          min={1}
          mb="md"
        />

        <Button fullWidth mt="lg" onClick={handleSave} loading={saving}>
          Сохранить
        </Button>

        {error && (
          <Notification color="red" mt="md">
            {error}
          </Notification>
        )}
      </Container>
    </Layout>
  );
}
