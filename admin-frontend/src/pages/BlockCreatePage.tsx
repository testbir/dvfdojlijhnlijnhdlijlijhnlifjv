// admin-frontend/src/pages/BlockCreatePage.tsx (обновленная версия с поддержкой языков)

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { blocksApi, uploadApi } from '../services/adminApi';
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
  Text,
  Code,
  Paper,
} from '@mantine/core';

const blockTypes = [
  { value: 'text', label: 'Текст' },
  { value: 'video', label: 'Видео' },
  { value: 'code', label: 'Код' },
  { value: 'image', label: 'Изображение' },
];

// Поддерживаемые языки программирования
const SUPPORTED_LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'tsx', label: 'TypeScript React (TSX)' },
  { value: 'jsx', label: 'JavaScript React (JSX)' },
  { value: 'html', label: 'HTML' },
  { value: 'css', label: 'CSS' },
  { value: 'scss', label: 'SCSS' },
  { value: 'sql', label: 'SQL' },
  { value: 'json', label: 'JSON' },
  { value: 'yaml', label: 'YAML' },
  { value: 'bash', label: 'Bash/Shell' },
  { value: 'java', label: 'Java' },
  { value: 'csharp', label: 'C#' },
  { value: 'cpp', label: 'C++' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'php', label: 'PHP' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'markdown', label: 'Markdown' },
  { value: 'dockerfile', label: 'Dockerfile' },
  { value: 'plaintext', label: 'Plain Text' },
];

type BlockType = 'text' | 'video' | 'code' | 'image';
type Lang = typeof SUPPORTED_LANGUAGES[number]['value'];

export default function BlockCreatePage() {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();

  const [type, setType] = useState<BlockType>('text');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [order, setOrder] = useState(1);
  const [language, setLanguage] = useState<Lang>('plaintext');
  const [videoPreview, setVideoPreview] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loadingUpload, setLoadingUpload] = useState(false);
  const [videoProcessing, setVideoProcessing] = useState(false);
  const [videoProcessingProgress, setVideoProcessingProgress] = useState(0);

  const handleFileUpload = async (file: File) => {
    try {
      setLoadingUpload(true);
      setError(null);
      const res = await uploadApi.uploadImage(file);      // ⬅️
      const url = res?.url || res?.image || '';
      if (!url) throw new Error('Сервер не вернул ссылку');
      setContent(url);
    } catch (e) {
      console.error(e);
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

      // прогресс аплоада можно повесить на axios, если нужно — тогда добавь обертку в uploadApi
      const res = await uploadApi.uploadVideo(file);      // ⬅️
      // ожидаем поле master_playlist_url или url
      const url = res?.master_playlist_url || res?.url || '';
      if (!url) throw new Error('Сервер не вернул URL мастер-плейлиста');

      // симулированный прогресс обработки
      for (let i = 50; i <= 100; i += 10) {
        // @ts-ignore
        await new Promise(r => setTimeout(r, 500));
        setVideoProcessingProgress(i);
      }
      setContent(url);
    } catch (e) {
      console.error(e);
      setError('Ошибка при загрузке и обработке видео');
    } finally {
      setVideoProcessing(false);
      setVideoProcessingProgress(0);
    }
  };

  const handleVideoPreviewUpload = async (file: File) => {
    try {
      setLoadingUpload(true);
      const res = await uploadApi.uploadImage(file, 'video-previews'); // ⬅️
      const url = res?.url || res?.image || '';
      setVideoPreview(url);
    } catch (e) {
      console.error(e);
      setError('Ошибка при загрузке превью');
    } finally {
      setLoadingUpload(false);
    }
  };

  const handleSubmit = async () => {
    if (!moduleId) { setError('Не указан ID модуля'); return; }
    try {
      await blocksApi.createBlock(Number(moduleId), {
        type,
        title,
        content: content.trim(),
        order,
        language: type === 'code' ? language : undefined,
        video_preview: type === 'video' ? (videoPreview.trim() || undefined) : undefined,
      });                                                // ⬅️
      navigate(-1);
    } catch (e) {
      console.error(e);
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
          onChange={(val) => setType((val as BlockType) || 'text')}
          mb="md"
        />

        <TextInput
          label="Заголовок"
          value={title}
          onChange={(e) => setTitle(e.currentTarget.value)}
          mb="md"
        />

        {type === 'text' && (
          <Textarea
            label="Контент"
            value={content}
            onChange={(e) => setContent(e.currentTarget.value)}
            mb="md"
            autosize
            minRows={5}
          />
        )}

        {type === 'code' && (
          <>
            <Select
              label="Язык программирования"
              data={SUPPORTED_LANGUAGES}
              value={language}
              onChange={(val) => setLanguage((val as Lang) || 'plaintext')}
              mb="md"
              searchable
              nothingFoundMessage="Язык не найден"
              description="Выберите язык для правильной подсветки синтаксиса"
            />
            
            <Textarea
              label="Код"
              value={content}
              onChange={(e) => setContent(e.currentTarget.value)}
              mb="md"
              autosize
              minRows={10}
              styles={{
                input: { 
                  fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace',
                  fontSize: '14px'
                }
              }}
              description={`Введите код на ${SUPPORTED_LANGUAGES.find(l => l.value === language)?.label}`}
            />

            {content && (
              <Paper shadow="xs" p="md" mb="md" withBorder>
              <Text size="sm" fw={500} mb="xs">Предпросмотр:</Text>
                <Code block style={{ 
                  maxHeight: 200, 
                  overflow: 'auto',
                  fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace' 
                }}>
                  {content}
                </Code>
              </Paper>
            )}
          </>
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
              accept="video/mp4,video/webm,video/quicktime"
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
          onChange={(v) => setOrder((v as number) || 1)}
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