// admin-frontend/src/pages/CourseCreatePage.tsx

import Layout from '../components/Layout';
import {
  Container,
  Title,
  TextInput,
  Textarea,
  NumberInput,
  Switch,
  Button,
  Group,
  Notification,
  FileInput,
  Loader,
  Image,
  Alert,
  Progress,
} from '@mantine/core';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { createCourse } from '../api/coursesApi';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axiosInstance';
import { DateTimePicker } from '@mantine/dates';

const schema = z.object({
  title: z.string().min(1, 'Введите название курса'),
  short_description: z.string().optional(),
  full_description: z.string().optional(),
  image: z.string().optional(),
  is_free: z.boolean(),
  price: z.number().optional(),
  discount: z.number().optional(),
  video: z.string().optional(), // Теперь это будет HLS URL
  video_preview: z.string().optional(),
  banner_text: z.string().optional(),
  banner_color_left: z.string().optional(),
  banner_color_right: z.string().optional(),
  group_title: z.string().optional(),
  order: z.number().min(0, 'Порядок должен быть ≥ 0').optional(),
  discount_start: z.date().optional(),
  discount_until: z.date().optional(),
});

type FormData = z.infer<typeof schema>;

export default function CourseCreatePage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loadingUpload, setLoadingUpload] = useState(false);
  const [videoProcessing, setVideoProcessing] = useState(false);
  const [videoProcessingProgress, setVideoProcessingProgress] = useState(0);

  const { control, handleSubmit, watch, setValue } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: '',
      short_description: '',
      full_description: '',
      image: '',
      is_free: false,
      price: undefined,
      discount: 0,
      video: '',
      video_preview: '',
      banner_text: '',
      banner_color_left: '',
      banner_color_right: '',
      group_title: '',
      order: 0,
      discount_start: undefined,
      discount_until: undefined,
    },
  });

  const isFree = watch('is_free');
  const imageUrl = watch('image');
  const videoUrl = watch('video');

  const handleUpload = async (file: File | null, isContent: boolean = false): Promise<string | null> => {
    if (!file) return null;
    try {
      setLoadingUpload(true);
      const formData = new FormData();
      formData.append('file', file);
      const url = isContent ? '/admin/upload/content' : '/admin/upload/public';
      const res = await axios.post(url, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data.url;
    } catch {
      setError('Ошибка при загрузке файла');
      return null;
    } finally {
      setLoadingUpload(false);
    }
  };

  const handleVideoUpload = async (file: File | null): Promise<void> => {
    if (!file) return;
    
    try {
      setVideoProcessing(true);
      setVideoProcessingProgress(0);
      setError(null);
      
      const formData = new FormData();
      formData.append('file', file);
      
      // Используем новый эндпоинт для видео
      const res = await axios.post('/admin/upload/video-direct', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadProgress = Math.round((progressEvent.loaded * 50) / progressEvent.total);
            setVideoProcessingProgress(uploadProgress);
          }
        }
      });

      // Симулируем прогресс обработки (в реальном приложении это должно приходить от сервера)
      for (let i = 50; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setVideoProcessingProgress(i);
      }

      if (res.data.master_playlist_url) {
        setValue('video', res.data.master_playlist_url);
        console.log('✅ Видео успешно обработано:', res.data);
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

  const onSubmit = async (data: FormData) => {
    try {
      const cleanedData = {
        ...data,
        short_description: data.short_description?.trim() || undefined,
        full_description: data.full_description?.trim() || undefined,
        image: data.image?.trim() || undefined,
        video: data.video?.trim() || undefined,
        video_preview: data.video_preview?.trim() || undefined,
        banner_text: data.banner_text?.trim() || undefined,
        banner_color_left: data.banner_color_left?.trim() || undefined,
        banner_color_right: data.banner_color_right?.trim() || undefined,
        group_title: data.group_title?.trim() || undefined,
      };
      await createCourse(cleanedData);
      navigate('/');
    } catch {
      setError('Ошибка при создании курса');
    }
  };

  return (
    <Layout>
      <Container size="sm">
        <Title order={2} ta="center" mb="lg">Создание курса</Title>

        {error && (
          <Notification color="red" mb="lg" onClose={() => setError(null)}>
            {error}
          </Notification>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <Controller
            name="title"
            control={control}
            render={({ field }) => <TextInput label="Название" required {...field} mb="md" />}
          />

          <Controller
            name="group_title"
            control={control}
            render={({ field }) => (
              <TextInput label="Группа курса" placeholder="Например: Python-разработчик" {...field} mb="md" />
            )}
          />

          <Controller
            name="order"
            control={control}
            render={({ field }) => (
              <NumberInput
                label="Положение (чем меньше, тем выше в списке)"
                value={field.value ?? 0}
                onChange={field.onChange}
                min={0}
                mb="md"
              />
            )}
          />

          <Controller
            name="short_description"
            control={control}
            render={({ field }) => <Textarea label="Краткое описание" {...field} mb="md" />}
          />

          <Controller
            name="full_description"
            control={control}
            render={({ field }) => <Textarea label="Полное описание" {...field} mb="md" />}
          />

          <FileInput
            label="Изображение курса"
            placeholder="Загрузите файл"
            accept="image/png,image/jpeg,image/webp"
            onChange={async (file) => {
              if (file) {
                const url = await handleUpload(file, false);
                if (url) setValue('image', url);
              }
            }}
            mb="md"
          />
          {imageUrl && <Image src={imageUrl} alt="Preview" height={200} radius="md" mb="md" />}

          <Controller
            name="is_free"
            control={control}
            render={({ field }) => (
              <Switch
                label="Бесплатный курс"
                checked={field.value}
                onChange={(e) => field.onChange(e.currentTarget.checked)}
                mb="md"
              />
            )}
          />

          {!isFree && (
            <>
              <Controller
                name="price"
                control={control}
                render={({ field }) => (
                  <NumberInput
                    label="Цена (₽)"
                    value={field.value ?? ''}
                    onChange={field.onChange}
                    min={0}
                    mb="md"
                  />
                )}
              />
              <Controller
                name="discount"
                control={control}
                render={({ field }) => (
                  <NumberInput
                    label="Скидка (%)"
                    value={field.value ?? ''}
                    onChange={field.onChange}
                    min={0}
                    max={100}
                    mb="md"
                  />
                )}
              />
            </>
          )}

          <Controller
            name="discount_start"
            control={control}
            render={({ field }) => (
              <DateTimePicker
                label="Начало скидки"
                placeholder="Выберите дату и время"
                value={field.value}
                onChange={field.onChange}
                mb="md"
              />
            )}
          />

          <Controller
            name="discount_until"
            control={control}
            render={({ field }) => (
              <DateTimePicker
                label="Окончание скидки"
                placeholder="Выберите дату и время"
                value={field.value}
                onChange={field.onChange}
                mb="md"
              />
            )}
          />


          {/* Новый блок для загрузки видео */}
          <Alert color="blue" mb="md">
            <strong>🎥 Загрузка видео курса</strong>
            <br />
            Видео будет автоматически обработано в разных качествах для оптимального воспроизведения.
            Поддерживаемые форматы: MP4, WebM, MOV (рекомендуется MP4).
          </Alert>

          <FileInput
            label="Видео курса (опционально)"
            description="Видео будет обработано и разбито на несколько качеств"
            accept="video/mp4,video/webm,video/mov"
            onChange={handleVideoUpload}
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

          {videoUrl && (
            <Alert color="green" mb="md">
              ✅ Видео успешно загружено и обработано!
              <br />
              <small>Мастер-плейлист: {videoUrl}</small>
            </Alert>
          )}

          {videoUrl && (
            <FileInput
              label="Превью к видео (опционально)"
              description="Изображение, которое показывается до начала воспроизведения"
              accept="image/png,image/jpeg,image/webp"
              onChange={async (file) => {
                if (file) {
                  const url = await handleUpload(file, true);
                  if (url) setValue('video_preview', url);
                }
              }}
              mb="md"
            />
          )}

          <Controller
            name="banner_text"
            control={control}
            render={({ field }) => (
              <TextInput
                label="Текст баннера"
                placeholder="Например: Лучший курс по Python!"
                {...field}
                mb="md"
              />
            )}
          />

          <Controller
            name="banner_color_left"
            control={control}
            render={({ field }) => (
              <TextInput label="Цвет слева (hex)" placeholder="#FF0000" {...field} mb="md" />
            )}
          />

          <Controller
            name="banner_color_right"
            control={control}
            render={({ field }) => (
              <TextInput label="Цвет справа (hex)" placeholder="#0000FF" {...field} mb="md" />
            )}
          />

          {(loadingUpload || videoProcessing) && <Loader size="sm" mb="md" />}

          <Group justify="center" mt="xl">
            <Button type="submit" disabled={loadingUpload || videoProcessing}>
              Создать курс
            </Button>
          </Group>
        </form>
      </Container>
    </Layout>
  );
}