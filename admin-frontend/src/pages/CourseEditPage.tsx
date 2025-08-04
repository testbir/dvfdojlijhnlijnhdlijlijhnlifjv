// src/pages/CourseEditPage.tsx


import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../api/axiosInstance';
import { DateTimePicker } from '@mantine/dates';
import '@mantine/dates/styles.css';
import dayjs from 'dayjs';


import {
  Container,
  Title,
  TextInput,
  Textarea,
  NumberInput,
  Button,
  Loader,
  Center,
  Notification,
  Switch,
  FileInput,
  Image,
  Alert,
  Progress,
} from '@mantine/core';
import Layout from '../components/Layout';

interface Course {
  id: number;
  title: string;
  short_description?: string;
  full_description?: string;
  image?: string;
  is_free: boolean;
  price?: number;
  discount?: number;
  video?: string;
  video_preview?: string;
  banner_text?: string;
  banner_color_left?: string;
  banner_color_right?: string;
  group_title?: string;
  order?: number;
  discount_start?: string;
  discount_until?: string;
}

export default function CourseEditPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [videoProcessing, setVideoProcessing] = useState(false);
  const [videoProcessingProgress, setVideoProcessingProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const res = await axios.get(`/admin/courses/${courseId}`);
        console.log("Курс с сервера:", res.data); // ← проверь поля discount_start/discount_until
        setCourse(res.data);
      } catch {
        setError('Ошибка при загрузке курса');
      } finally {
        setLoading(false);
      }
    };
    fetchCourse();
  }, [courseId]);


  const uploadFile = async (file: File, isContent: boolean) => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      const url = isContent ? '/admin/upload/content' : '/admin/upload/public';
      const res = await axios.post(url, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    } catch {
      setError('Ошибка при загрузке файла');
      return null;
    } finally {
      setUploading(false);
    }
  };

  // 🎬 Новая функция для загрузки и обработки видео (как в CourseCreatePage)
  // admin-frontend/src/pages/CourseEditPage.tsx - ЗАМЕНИТЕ ФУНКЦИЮ handleVideoUpload:

const handleVideoUpload = async (file: File | null): Promise<void> => {
  if (!file) return;
  
  try {
    setVideoProcessing(true);
    setVideoProcessingProgress(0);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await axios.post('/admin/upload/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000, // 1 минута только на загрузку
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const uploadProgress = Math.round((progressEvent.loaded * 30) / progressEvent.total);
          setVideoProcessingProgress(uploadProgress);
        }
      }
    });

    if (res.data.video_id) {
      // Опрашиваем статус обработки видео
      const finalResult = await pollVideoStatus(res.data.video_id);
      if (finalResult) {
        setCourse(prev => prev ? { ...prev, video: finalResult } : prev);
        console.log('✅ Видео успешно обработано:', finalResult);
      }
    }
    
  } catch (err) {
    console.error('Ошибка при загрузке видео:', err);
    setError('Ошибка при загрузке видео');
  } finally {
    setVideoProcessing(false);
    setVideoProcessingProgress(0);
  }
};

const pollVideoStatus = async (videoId: string): Promise<string | null> => {
  const maxAttempts = 120; // 20 минут максимум (120 * 10 секунд)
  
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const statusRes = await axios.get(`/admin/video-status/${videoId}`);
      const status = statusRes.data;
      
      // Обновляем прогресс
      const progress = 30 + Math.round((i / maxAttempts) * 70);
      setVideoProcessingProgress(Math.min(progress, 95));
      
      if (status.status === 'completed' && status.result?.master_playlist_url) {
        setVideoProcessingProgress(100);
        return status.result.master_playlist_url;
      }
      
      if (status.status === 'failed') {
        throw new Error(status.error || 'Ошибка обработки видео');
      }
      
      // Ждем 10 секунд перед следующей попыткой
      await new Promise(resolve => setTimeout(resolve, 10000));
      
    } catch (err: any) {
      // Если это не ошибка статуса, а проблема с сетью, пробуем еще раз
      if (i > 5 && err.response?.status !== 404) {
        throw err;
      }
      await new Promise(resolve => setTimeout(resolve, 10000));
    }
  }
  
  throw new Error('Превышено время ожидания обработки видео');
};

  const handleSave = async () => {
    if (!course) return;
    setSaving(true);
    try {
      await axios.put(`/admin/courses/${courseId}`, {
        title: course.title?.trim(),
        short_description: course.short_description?.trim() || undefined,
        full_description: course.full_description?.trim() || undefined,
        image: course.image?.trim() || undefined,
        is_free: course.is_free,
        price: course.is_free ? undefined : course.price ?? 0,
        discount: course.is_free ? undefined : course.discount ?? 0,
        video: course.video?.trim() || undefined,
        video_preview: course.video_preview?.trim() || undefined,
        banner_text: course.banner_text?.trim() || undefined,
        banner_color_left: course.banner_color_left?.trim() || undefined,
        banner_color_right: course.banner_color_right?.trim() || undefined,
        group_title: course.group_title?.trim() || undefined,
        order: course.order ?? 0,
        discount_start: course.discount_start ?? undefined,
        discount_until: course.discount_until ?? undefined,

      });
      navigate('/');
    } catch {
      setError('Ошибка при сохранении');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Center><Loader /></Center>
      </Layout>
    );
  }

  if (error && !course) {
    return (
      <Layout>
        <Notification color="red">{error}</Notification>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container size="sm">
        <Title order={2} ta="center" mb="lg">Редактирование курса</Title>

        {error && (
          <Notification color="red" mb="lg" onClose={() => setError(null)}>
            {error}
          </Notification>
        )}

        <TextInput
          label="Название"
          value={course?.title || ''}
          onChange={(e) => setCourse({ ...course!, title: e.currentTarget.value })}
          mb="md"
        />

        <TextInput
          label="Группа курса"
          value={course?.group_title || ''}
          onChange={(e) => setCourse({ ...course!, group_title: e.currentTarget.value })}
          mb="md"
        />

        <NumberInput
          label="Порядок (чем меньше, тем выше курс)"
          value={course?.order ?? 0}
          onChange={(val) => setCourse({ ...course!, order: typeof val === 'number' ? val : 0 })}
          min={0}
          mb="md"
        />

        <Textarea
          label="Краткое описание"
          value={course?.short_description || ''}
          onChange={(e) => setCourse({ ...course!, short_description: e.currentTarget.value })}
          mb="md"
        />

        <Textarea
          label="Полное описание"
          value={course?.full_description || ''}
          onChange={(e) => setCourse({ ...course!, full_description: e.currentTarget.value })}
          autosize
          minRows={4}
          mb="md"
        />

        <FileInput
          label="Новое изображение"
          accept="image/png,image/jpeg,image/webp"
          onChange={async (file) => {
            if (file) {
              const res = await uploadFile(file, false);
              if (res?.url) setCourse((prev) => prev ? { ...prev, image: res.url } : prev);
            }
          }}
          mb="md"
        />
        {uploading && <Loader size="sm" mb="md" />}
        {course?.image && <Image src={course.image} alt="Превью" height={200} radius="md" mb="xs" />}
        <TextInput
          label="Ссылка на изображение"
          value={course?.image || ''}
          onChange={(e) => setCourse({ ...course!, image: e.currentTarget.value })}
          mb="md"
        />

        <Switch
          label="Бесплатный курс"
          checked={course?.is_free || false}
          onChange={(e) => setCourse({ ...course!, is_free: e.currentTarget.checked })}
          mb="md"
        />


        {!course?.is_free && (
        <>
          <NumberInput
            label="Цена"
            value={course?.price ?? 0}
            onChange={(val) => setCourse({ ...course!, price: val as number })}
            mb="md"
          />
          <NumberInput
            label="Скидка"
            value={course?.discount ?? 0}
            onChange={(val) => setCourse({ ...course!, discount: val as number })}
            mb="md"
          />

          <DateTimePicker
            label="Начало скидки"
            placeholder="Выберите дату и время"
            value={course?.discount_start ? dayjs(course.discount_start).toDate() : null}
            onChange={(val) =>
              setCourse({
                ...course!,
                discount_start: val ? dayjs(val).toISOString() : undefined,
              })
            }
            valueFormat="DD.MM.YYYY HH:mm"
            mb="md"
          />

          <DateTimePicker
            label="Окончание скидки"
            placeholder="Выберите дату и время"
            value={course?.discount_until ? dayjs(course.discount_until).toDate() : null}
            onChange={(val) =>
              setCourse({
                ...course!,
                discount_until: val ? dayjs(val).toISOString() : undefined,
              })
            }
            valueFormat="DD.MM.YYYY HH:mm"
            mb="md"
          />



        <Button
            color="red"
            variant="outline"
            onClick={() =>
              setCourse((prev) =>
                prev
                  ? {
                      ...prev,
                      discount: 0,
                      discount_start: undefined,
                      discount_until: undefined,
                    }
                  : prev
              )
            }
            mb="md"
        >
            Отменить скидку
        </Button>






        </>
      )}


        {/* 🎬 Обновленная секция видео с HLS обработкой */}
        <Alert color="blue" mb="md">
          <strong>🎥 Замена видео курса</strong>
          <br />
          Новое видео будет автоматически обработано в разных качествах для оптимального воспроизведения.
          Поддерживаемые форматы: MP4, WebM, MOV (рекомендуется MP4).
        </Alert>

        <FileInput
          label="Заменить видео курса"
          description="Видео будет обработано и разбито на несколько качеств"
          accept="video/mp4,video/webm,video/mov"
          onChange={handleVideoUpload}
          disabled={videoProcessing || uploading}
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

        {course?.video && (
          <>
            {course.video.includes('.m3u8') ? (
              <Alert color="green" mb="md">
                ✅ HLS видео подключено!
                <br />
                <small>Мастер-плейлист: {course.video}</small>
              </Alert>
            ) : (
              <Alert color="orange" mb="md">
                ⚠️ Обычное видео (рекомендуется заменить на HLS)
              </Alert>
            )}
            <TextInput
              label="URL видео (HLS мастер-плейлист или обычное видео)"
              value={course.video}
              onChange={(e) => setCourse((prev) => prev ? { ...prev, video: e.currentTarget.value } : prev)}
              mb="md"
            />
          </>
        )}

        <FileInput
          label="Заменить превью к видео (jpg/png/webp)"
          accept="image/png,image/jpeg,image/webp"
          onChange={async (file) => {
            if (file) {
              const res = await uploadFile(file, true);
              if (res?.url) setCourse((prev) => prev ? { ...prev, video_preview: res.url } : prev);
            }
          }}
          mb="md"
        />
        {course?.video_preview && (
          <>
            <Image src={course.video_preview} alt="Превью" height={120} radius="sm" mb="xs" />
            <TextInput
              label="Ссылка на превью"
              value={course.video_preview}
              onChange={(e) => setCourse((prev) => prev ? { ...prev, video_preview: e.currentTarget.value } : prev)}
              mb="md"
            />
          </>
        )}

        <TextInput
          label="Текст баннера"
          value={course?.banner_text || ''}
          onChange={(e) => setCourse({ ...course!, banner_text: e.currentTarget.value })}
          mb="md"
        />
        <TextInput
          label="Цвет слева (hex)"
          value={course?.banner_color_left || ''}
          onChange={(e) => setCourse({ ...course!, banner_color_left: e.currentTarget.value })}
          mb="md"
        />
        <TextInput
          label="Цвет справа (hex)"
          value={course?.banner_color_right || ''}
          onChange={(e) => setCourse({ ...course!, banner_color_right: e.currentTarget.value })}
          mb="md"
        />

        <Button 
          fullWidth 
          onClick={handleSave} 
          loading={saving} 
          disabled={videoProcessing || uploading}
        >
          Сохранить
        </Button>
      </Container>
    </Layout>
  );
}
