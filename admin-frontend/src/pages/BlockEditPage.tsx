// admin-frontend/src/pages/BlockEditPage.tsx (обновленная версия с поддержкой языков)

import { useEffect, useState } from 'react';
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


type BlockType = 'text' | 'video' | 'code' | 'image';
type Lang = typeof SUPPORTED_LANGUAGES[number]['value'];


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
        const res = await blocksApi.getBlock(Number(blockId));
          if (res.type === 'code' && !res.language) res.language = 'plaintext';
          setBlock(res);
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
    const res = await uploadApi.uploadImage(file);

    setBlock((prev: any) => (
      { ...prev, content: res?.url || res?.image }
    ));

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

      const res = await uploadApi.uploadVideo(file);

      // имитация прогресса обработки
      for (let i = 50; i <= 100; i += 10) {
        await new Promise(r => setTimeout(r, 500));
        setVideoProcessingProgress(i);
      }

      const url = res?.master_playlist_url || res?.url;
      if (!url) throw new Error('Сервер не вернул URL мастер-плейлиста');

      setBlock((prev: any) => ({ ...prev, content: url }));
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
      const res = await uploadApi.uploadImage(file, 'video-previews');
        
      setBlock((prev: any) => (
        { ...prev, video_preview: res?.url || res?.image }
      ));
    
    } catch {
      setError('Ошибка при загрузке превью');
    } finally {
      setUploading(false);
    }
  };

  const handleSave = async () => {
    const id = Number(blockId);
    if (!id) {
      setError('Некорректный ID блока');
      return;
    }
    setSaving(true);
    try {
      await blocksApi.updateBlock(id, {
        type: block.type as BlockType,
        title: String(block.title || ''),
        content: String(block.content || '').trim(),
        order: Number(block.order || 1),
        language: block.type === 'code' ? block.language : undefined,
        video_preview:
          block.type === 'video'
            ? (String(block.video_preview || '').trim() || undefined)
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
          onChange={(val) => {
            const t = (val as BlockType) || 'text';
            setBlock({
              ...block,
              type: t,
              language: t === 'code' ? (block.language || 'plaintext') : undefined,
            });
          }}
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
              onChange={(val) => setBlock({ ...block, language: (val as Lang) || 'plaintext' })}
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
              accept="video/mp4,video/webm,video/quicktime"
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
          onChange={(v) => setBlock({ ...block, order: Number(v) || 1 })}
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