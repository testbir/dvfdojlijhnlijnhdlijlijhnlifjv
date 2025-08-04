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
  Alert
} from '@mantine/core';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { createCourse } from '../api/coursesApi';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axiosInstance';
import { DateTimePicker } from '@mantine/dates';

/* ------------------ схема формы ------------------ */
const schema = z.object({
  title: z.string().min(1, 'Введите название курса'),
  short_description: z.string().optional(),
  full_description: z.string().optional(),
  image: z.string().optional(),
  is_free: z.boolean(),
  price: z.number().optional(),
  discount: z.number().optional(),
  video: z.string().optional(),       // теперь это прямой URL .mp4 /.webm
  video_preview: z.string().optional(),
  banner_text: z.string().optional(),
  banner_color_left: z.string().optional(),
  banner_color_right: z.string().optional(),
  group_title: z.string().optional(),
  order: z.number().min(0, 'Порядок должен быть ≥ 0').optional(),
  discount_start: z.date().optional(),
  discount_until: z.date().optional()
});
type FormData = z.infer<typeof schema>;

/* ================================================= */
export default function CourseCreatePage() {
  const navigate = useNavigate();

  /* ---------- local state ---------- */
  const [error, setError] = useState<string | null>(null);
  const [loadingUpload, setLoadingUpload] = useState(false);

  /* ---------- react-hook-form ---------- */
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
      discount_until: undefined
    }
  });

  /* ---------- watchers ---------- */
  const isFree   = watch('is_free');
  const imageUrl = watch('image');
  const videoUrl = watch('video');

  /* ---------- generic file upload ---------- */
  const handleUpload = async (file: File | null, isContent = false): Promise<string | null> => {
    if (!file) return null;
    try {
      setLoadingUpload(true);
      const formData = new FormData();
      formData.append('file', file);

      const endpoint = '/admin/upload/public';
      const res = await axios.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return res.data.url as string;
    } catch {
      setError('Ошибка при загрузке файла');
      return null;
    } finally {
      setLoadingUpload(false);
    }
  };

  /* ---------- видео: простой public-upload, БЕЗ HLS ---------- */
  const handleVideoUpload = async (file: File | null): Promise<void> => {
    if (!file) return;
    try {
      setLoadingUpload(true);
      const formData = new FormData();
      formData.append('file', file);

      const res = await axios.post('/admin/upload/video-simple-public', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (pe) => {
          if (pe.total) {
            const percent = Math.round((pe.loaded / pe.total) * 100);
            console.log(`video upload: ${percent}%`);
          }
        }
      });

      /* прямой CDN-URL .mp4 /.webm */
      setValue('video', res.data.url);
    } catch {
      setError('Ошибка при загрузке видео');
    } finally {
      setLoadingUpload(false);
    }
  };

  /* ---------- submit ---------- */
  const onSubmit = async (data: FormData) => {
    try {
      await createCourse({
        ...data,
        short_description : data.short_description?.trim()  || undefined,
        full_description  : data.full_description?.trim()   || undefined,
        image             : data.image?.trim()              || undefined,
        video             : data.video?.trim()              || undefined,
        video_preview     : data.video_preview?.trim()      || undefined,
        banner_text       : data.banner_text?.trim()        || undefined,
        banner_color_left : data.banner_color_left?.trim()  || undefined,
        banner_color_right: data.banner_color_right?.trim() || undefined,
        group_title       : data.group_title?.trim()        || undefined
      });
      navigate('/');
    } catch (err) {
      console.error(err);
      setError('Ошибка при создании курса');
    }
  };

  /* ========================================================== */
  return (
    <Layout>
      <Container size="sm">
        <Title order={2} ta="center" mb="lg">
          Создание курса
        </Title>

        {error && (
          <Notification color="red" mb="lg" onClose={() => setError(null)}>
            {error}
          </Notification>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          {/* ---------- название ---------- */}
          <Controller
            name="title"
            control={control}
            render={({ field }) => (
              <TextInput label="Название" required {...field} mb="md" />
            )}
          />

          {/* ---------- группа ---------- */}
          <Controller
            name="group_title"
            control={control}
            render={({ field }) => (
              <TextInput
                label="Группа курса"
                placeholder="Например: Python-разработчик"
                {...field}
                mb="md"
              />
            )}
          />

          {/* ---------- порядок ---------- */}
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

          {/* ---------- описания ---------- */}
          <Controller
            name="short_description"
            control={control}
            render={({ field }) => (
              <Textarea label="Краткое описание" {...field} mb="md" />
            )}
          />
          <Controller
            name="full_description"
            control={control}
            render={({ field }) => (
              <Textarea label="Полное описание" {...field} mb="md" />
            )}
          />

          {/* ---------- картинка ---------- */}
          <FileInput
            label="Изображение курса"
            placeholder="Загрузите файл"
            accept="image/png,image/jpeg,image/webp"
            onChange={async (file) => {
              const url = await handleUpload(file, false);
              if (url) setValue('image', url);
            }}
            mb="md"
          />
          {imageUrl && (
            <Image src={imageUrl} alt="preview" height={200} radius="md" mb="md" />
          )}

          {/* ---------- бесплатный / платный ---------- */}
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

          {/* ---------- даты скидки ---------- */}
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

          {/* ---------- видео ---------- */}
          <Alert color="blue" mb="md">
            <strong>🎥 Загрузка видео курса</strong>
            <br />
            Файл будет сохранён «как есть» (без HLS). Поддерживаются MP4, WebM, MOV.
          </Alert>

          <FileInput
            label="Видео курса (опционально)"
            accept="video/mp4,video/webm,video/mov"
            onChange={handleVideoUpload}
            disabled={loadingUpload}
            mb="md"
          />

          {videoUrl && (
            <Alert color="green" mb="md">
              ✅ Видео загружено
              <br />
              <small>{videoUrl}</small>
            </Alert>
          )}

          {videoUrl && (
            <FileInput
              label="Превью к видео (опционально)"
              description="Изображение, отображаемое до начала воспроизведения"
              accept="image/png,image/jpeg,image/webp"
              onChange={async (file) => {
                const url = await handleUpload(file, true);
                if (url) setValue('video_preview', url);
              }}
              mb="md"
            />
          )}

          {/* ---------- баннер ---------- */}
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

          {loadingUpload && <Loader size="sm" mb="md" />}

          {/* ---------- submit ---------- */}
          <Group justify="center" mt="xl">
            <Button type="submit" disabled={loadingUpload}>
              Создать курс
            </Button>
          </Group>
        </form>
      </Container>
    </Layout>
  );
}
