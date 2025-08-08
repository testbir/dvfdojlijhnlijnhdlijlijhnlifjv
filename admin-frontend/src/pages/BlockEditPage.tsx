// admin-frontend/src/pages/BlockEditPage.tsx (обновленная версия с поддержкой языков)

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
  Alert,
  Progress,
  Code,
  Paper,
  Text,
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

export default function BlockEditPage() {
  const { blockId } = useParams<{ blockId: string }>();
  const navigate = useNavigate();

  const [block, setBlock] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [videoProcessing, setVideoProcessing] = useState(false);
  const [videoProcessingProgress, setVideoProcessingProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBlock = async () => {
      try {
        const res = await axios.get(`/admin/blocks/${blockId}`);
        // Если язык не указан для блока кода, устанавливаем по умолчанию
        if (res.data.type === 'code' && !res.data.language) {
          res.data.language = 'plaintext';
        }
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

  const handleVideoUpload = async (file: File) => {
    try {
      setVideoProcessing(true);
      setVideoProcessingProgress(0);
      setError(null);
      
      const formData = new FormData();
      formData.append('file', file);
      
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
        setBlock((prev: any) => ({
          ...prev,
          content: response.data.master_playlist_url,
        }));
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
        language: block.type === 'code' ? block.language : undefined, // Добавляем язык
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

  if (!block) {
    return (
      <Layout>
        <Notification color="red">Блок не найден</Notification>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container size="sm">
        <Title order={2} ta="center" mb="lg">
          Редактирование блока
        </Title>

        {error && (
          <Notification color="red" mb="lg" onClose={() => setError(null)}>
            {error}
          </Notification>
        )}

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

        {block.type === 'text' && (
          <Textarea
            label="Контент"
            value={block.content}
            onChange={(e) => setBlock({ ...block, content: e.currentTarget.value })}
            mb="md"
            autosize
            minRows={5}
          />
        )}

        {block.type === 'code' && (
          <>
            <Select
              label="Язык программирования"
              data={SUPPORTED_LANGUAGES}
              value={block.language || 'plaintext'}
              onChange={(val) => setBlock({ ...block, language: val! })}
              mb="md"
              searchable
              nothingFoundMessage="Язык не найден" 
              description="Выберите язык для правильной подсветки синтаксиса"
            />
            
            <Textarea
              label="Код"
              value={block.content}
              onChange={(e) => setBlock({ ...block, content: e.currentTarget.value })}
              mb="md"
              autosize
              minRows={10}
              styles={{
                input: { 
                  fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace',
                  fontSize: '14px'
                }
              }}
              description={`Код на ${SUPPORTED_LANGUAGES.find(l => l.value === block.language)?.label || 'Plain Text'}`}
            />

            {block.content && (
              <Paper shadow="xs" p="md" mb="md" withBorder>
                <Text size="sm" fw={500} mb="xs"> Предпросмотр:</Text>
                <Code block style={{ 
                  maxHeight: 200, 
                  overflow: 'auto',
                  fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace' 
                }}>
                  {block.content}
                </Code>
              </Paper>
            )}
          </>
        )}

        {block.type === 'image' && (
          <>
            <FileInput
              label="Новое изображение"
              onChange={(file) => file && handleFileUpload(file)}
              accept="image/*"
              mb="md"
              disabled={uploading}
            />
            {uploading && <Loader size="sm" mb="md" />}
            {block.content && (
              <Image src={block.content} height={150} radius="sm" mb="md" />
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
            <Alert color="blue" mb="md">
              <strong>🎥 Загрузка видео</strong>
              <br />
              Видео будет автоматически обработано в разных качествах для оптимального воспроизведения.
            </Alert>

            <FileInput
              label="Новое видео"
              description="Будет создан HLS-поток с разными качествами"
              onChange={(file) => file && handleVideoUpload(file)}
              accept="video/*"
              mb="md"
              disabled={uploading || videoProcessing}
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

            {block.content && (
              <>
                <Alert color="green" mb="md">
                  ✅ Видео загружено
                  <br />
                  <small>HLS плейлист: {block.content}</small>
                </Alert>
                <TextInput
                  label="HLS мастер-плейлист URL"
                  value={block.content}
                  onChange={(e) => setBlock({ ...block, content: e.currentTarget.value })}
                  mb="md"
                />
              </>
            )}

            <FileInput
              label="Превью к видео"
              onChange={(file) => file && handleVideoPreviewUpload(file)}
              accept="image/*"
              mb="md"
              disabled={uploading}
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
      </Container>
    </Layout>
  );
}