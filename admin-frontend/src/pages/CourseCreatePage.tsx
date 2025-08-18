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
import { coursesApi, uploadApi } from '../services/adminApi';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DateTimePicker } from '@mantine/dates';

const numberOpt = (schema: z.ZodTypeAny) =>
  z.preprocess((v) => (v === '' ? undefined : v), schema);

const schema = z.object({
  title: z.string().min(1, 'Введите название курса'),
  short_description: z.string().min(1, 'Введите краткое описание'),
  full_description: z.string().optional(),
  image: z.string().optional(),
  is_free: z.boolean(),
  price: numberOpt(z.number().nonnegative()).optional(),
  discount: numberOpt(z.number().min(0).max(100)).optional(),
  video: z.string().optional(),
  video_preview: z.string().optional(),
  banner_text: z.string().optional(),
  banner_color_left: z.string().optional(),
  banner_color_right: z.string().optional(),
  group_title: z.string().optional(),
  order: numberOpt(z.number().min(0)).optional(),
  discount_start: z.date().optional(),
  discount_until: z.date().optional(),
}).superRefine((v, ctx) => {
  if (!v.is_free && (v.price === undefined || v.price === null)) {
    ctx.addIssue({ path: ['price'], code: z.ZodIssueCode.custom, message: 'Цена обязательна для платного курса' });
  }
});

type FormData = z.infer<typeof schema>;

export default function CourseCreatePage() {
  const navigate = useNavigate();

  const [error, setError] = useState<string | null>(null);
  const [loadingUpload, setLoadingUpload] = useState(false);

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

  const isFree   = watch('is_free');
  const imageUrl = watch('image');
  const videoUrl = watch('video');

  // загрузка изображений (курс/превью)
  const handleUpload = async (file: File | null): Promise<string | null> => {
    if (!file) return null;
    try {
      setLoadingUpload(true);
      const res = await uploadApi.uploadImage(file, 'courses'); // <- adminApi
      const url = res?.url || res?.image || '';
      if (!url) throw new Error('Сервер не вернул url');
      return url;
    } catch {
      setError('Ошибка при загрузке файла');
      return null;
    } finally {
      setLoadingUpload(false);
    }
  };

  // видео: через uploadApi (HLS с ожиданием обработки)
  const handleVideoUpload = async (file: File | null): Promise<void> => {
    if (!file) return;
    try {
      setLoadingUpload(true);
      const url = await uploadApi.uploadVideo(file); // <- adminApi (возвращает master_playlist_url)
      setValue('video', url);
    } catch {
      setError('Ошибка при загрузке видео');
    } finally {
      setLoadingUpload(false);
    }
  };

  const onSubmit = async (data: FormData) => {
    try {
      const createdCourse = await coursesApi.createCourse({
        ...data,
        discount_start: data.discount_start?.toISOString(),
        discount_until: data.discount_until?.toISOString(),
        short_description : data.short_description.trim(),
        full_description  : data.full_description?.trim()   || undefined,
        image             : data.image?.trim()              || undefined,
        video             : data.video?.trim()              || undefined,
        video_preview     : data.video_preview?.trim()      || undefined,
        banner_text       : data.banner_text?.trim()        || undefined,
        banner_color_left : data.banner_color_left?.trim()  || undefined,
        banner_color_right: data.banner_color_right?.trim() || undefined,
        group_title       : data.group_title?.trim()        || undefined
      });

      navigate(`/courses/${createdCourse.id}/structure`);
    } catch (err) {
      console.error(err);
      setError('Ошибка при создании курса');
    }
  };

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
          <Controller
            name="title"
            control={control}
            render={({ field }) => (
              <TextInput label="Название" required {...field} mb="md" />
            )}
          />

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

          <FileInput
            label="Изображение курса"
            placeholder="Загрузите файл"
            accept="image/png,image/jpeg,image/webp"
            onChange={async (file) => {
              const url = await handleUpload(file);
              if (url) setValue('image', url);
            }}
            mb="md"
          />
          {imageUrl && (
            <Image src={imageUrl} alt="preview" height={200} radius="md" mb="md" />
          )}

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

          <Alert color="blue" mb="md">
            <strong>🎥 Загрузка видео курса</strong>
            <br />
            Видео будет обработано (HLS) и доступно в нескольких качествах.
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
                const url = await handleUpload(file);
                if (url) setValue('video_preview', url);
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

          {loadingUpload && <Loader size="sm" mb="md" />}

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
