// admin-frontend/src/pages/BlockCreatePage.tsx (обновленная версия)

import { useState } from 'react';
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
  Notification,
  FileInput,
  Loader,
  Image,
  Alert,
  Progress,
} from '@mantine/core';

const blockTypes = [
  { value: 'text', label: 'Текст' },
  { value: 'video', label: 'Видео' },
  { value: 'code', label: 'Код' },
  { value: 'image', label: 'Изображение' },
];

export default function BlockCreatePage() {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();

  const [type, setType] = useState('text');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [order, setOrder] = useState(1);
  const [videoPreview, setVideoPreview] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loadingUpload, setLoadingUpload] = useState(false);
  const [videoProcessing, setVideoProcessing] = useState(false);
  const [videoProcessingProgress, setVideoProcessingProgress] = useState(0);

  const handleFileUpload = async (file: File) => {
    try {
      setLoadingUpload(true);
      setError(null);
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post('/admin/upload/content', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const result = response.data?.url || '';
      if (!result) throw new Error('Сервер не вернул ссылку');
      setContent(result);
    } catch (err) {
      console.error('Ошибка загрузки:', err);
      setError('Ошибка при загрузке файла');
    } finally {
      setLoadingUpload(false);
    }
  };

  const handleVideoUpload = async (file: File) => {
    try {
      setVideoProcessing(true);
      setVideoProcessingProgress(0);
      setError(null);
      
      const formData = new FormData();
      formData.append('file', file);
      
      // Используем новый эндпоинт для видео
      const response = await axios.post('/admin/upload/video-direct', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadProgress = Math.round((progressEvent.loaded * 50) / progressEvent.total);
            setVideoProcessingProgress(uploadProgress);
          }
        }
      });

      // Симулируем прогресс обработки
      for (let i = 50; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setVideoProcessingProgress(i);
      }

      if (response.data.master_playlist_url) {
        setContent(response.data.master_playlist_url);
        console.log('✅ Видео успешно обработано:', response.data);
      } else {
        throw new Error('Сервер не вернул URL мастер-плейлиста');
      }
      
    } catch (err) {
      console.error('Ошибка при загрузке видео:', err);
      setError('Ошибка при загрузке и обработке видео');
    } finally {
      setVideoProcessing(false);
      setVideoProcessingProgress(0);
    }
  };

  const handleVideoPreviewUpload = async (file: File) => {
    try {
      setLoadingUpload(true);
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post('/admin/upload/content', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const result = response.data?.url || '';
      setVideoPreview(result);
    } catch (err) {
      console.error('Ошибка загрузки превью:', err);
      setError('Ошибка при загрузке превью');
    } finally {
      setLoadingUpload(false);
    }
  };

  const handleSubmit = async () => {
    if (!moduleId) {
      setError('Не указан ID модуля');
      return;
    }

    try {
      await axios.post(`/admin/modules/${moduleId}/blocks/`, {
        type,
        title,
        content: content.trim(),
        order,
        video_preview: type === 'video' ? videoPreview.trim() || null : undefined,
      });
      navigate(-1);
    } catch (err) {
      console.error('Ошибка создания блока:', err);
      setError('Ошибка при создании блока');
    }
  };

  return (
    <Layout>
      <Container size="sm">
        <Title order={2} ta="center" mb="lg">Создание блока</Title>

        {error && (
          <Notification color="red" mb="lg" onClose={() => setError(null)}>
            {error}
          </Notification>
        )}

        <Select
          label="Тип блока"
          data={blockTypes}
          value={type}
          onChange={(val) => setType(val!)}
          mb="md"
        />

        <TextInput
          label="Заголовок"
          value={title}
          onChange={(e) => setTitle(e.currentTarget.value)}
          mb="md"
        />

        {(type === 'text' || type === 'code') && (
          <Textarea
            label="Контент"
            value={content}
            onChange={(e) => setContent(e.currentTarget.value)}
            mb="md"
            autosize
            minRows={3}
          />
        )}

        {type === 'image' && (
          <>
            <FileInput
              label="Изображение"
              onChange={(file) => file && handleFileUpload(file)}
              accept="image/png,image/jpeg,image/webp"
              disabled={loadingUpload}
              mb="md"
            />
            {loadingUpload && <Loader size="sm" mb="md" />}
            {content && (
              <>
                <Image src={content} height={150} radius="sm" mb="sm" />
                <TextInput
                  label="Ссылка на файл"
                  value={content}
                  onChange={(e) => setContent(e.currentTarget.value)}
                  mb="md"
                />
              </>
            )}
          </>
        )}

        {type === 'video' && (
          <>
            <Alert color="blue" mb="md">
              <strong>🎥 Загрузка видео</strong>
              <br />
              Видео будет автоматически обработано в разных качествах для оптимального воспроизведения.
              Поддерживаемые форматы: MP4, WebM, MOV.
            </Alert>

            <FileInput
              label="Видео файл"
              description="Будет создан HLS-поток с разными качествами"
              accept="video/mp4,video/webm,video/mov"
              onChange={(file) => file && handleVideoUpload(file)}
              disabled={videoProcessing || loadingUpload}
              mb="md"
            />

            {videoProcessing && (
              <div style={{ marginBottom: '1rem' }}>
                <Progress value={videoProcessingProgress} mb="xs" />
                <p style={{ fontSize: '14px', color: '#666' }}>
                  {videoProcessingProgress < 50 
                    ? `Загрузка видео... ${videoProcessingProgress}%`
                    : `Обработка видео... ${videoProcessingProgress}%`
                  }
                </p>
              </div>
            )}

            {content && (
              <Alert color="green" mb="md">
                ✅ Видео успешно загружено и обработано!
                <br />
                <small>HLS плейлист: {content}</small>
              </Alert>
            )}

            {content && (
              <TextInput
                label="HLS мастер-плейлист URL"
                value={content}
                onChange={(e) => setContent(e.currentTarget.value)}
                mb="md"
                description="URL будет автоматически заполнен после обработки видео"
              />
            )}

            <FileInput
              label="Превью к видео (необязательно)"
              accept="image/png,image/jpeg,image/webp"
              onChange={(file) => file && handleVideoPreviewUpload(file)}
              disabled={loadingUpload}
              mb="md"
            />
            {videoPreview && (
              <>
                <Image src={videoPreview} height={100} radius="sm" mb="xs" />
                <TextInput
                  label="Ссылка на превью"
                  value={videoPreview}
                  onChange={(e) => setVideoPreview(e.currentTarget.value)}
                  mb="md"
                />
              </>
            )}
          </>
        )}

        <NumberInput
          label="Порядок"
          value={order}
          onChange={(val) => setOrder(val as number)}
          min={1}
          mb="md"
        />

        <Button 
          fullWidth 
          mt="lg" 
          onClick={handleSubmit} 
          disabled={loadingUpload || videoProcessing}
          loading={loadingUpload || videoProcessing}
        >
          Создать блок
        </Button>
      </Container>
    </Layout>
  );
}