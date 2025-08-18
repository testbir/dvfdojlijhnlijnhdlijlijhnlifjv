// src/pages/BannerCreatePage.tsx

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { DateTimePicker } from '@mantine/dates';
import { bannersApi } from '../services/adminApi';

import {
  Container,
  Title,
  FileInput,
  NumberInput,
  Button,
  Notification,
  Loader,
  Image,
  TextInput,
} from '@mantine/core';

export default function BannerCreatePage() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [order, setOrder] = useState<number>(0);
  const [link, setLink] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [discountStart, setDiscountStart] = useState<Date | null>(null);
  const [discountUntil, setDiscountUntil] = useState<Date | null>(null);

  const handleSubmit = async () => {
    if (!file) {
      setError('Выберите изображение');
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('order', order.toString());
      formData.append('link', link);

      if (discountStart) {
        formData.append('discount_start', discountStart.toISOString());
      }
      if (discountUntil) {
        formData.append('discount_until', discountUntil.toISOString());
      }

      await bannersApi.createBanner(formData);
      navigate('/');
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Ошибка при создании баннера');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Layout>
      <Container size="sm">
        <Title order={2} ta="center" mb="lg">
          Добавить баннер
        </Title>

        <FileInput
          label="Изображение"
          accept="image/*"
          onChange={(f) => {
            setFile(f);
            setPreview(f ? URL.createObjectURL(f) : null);
          }}
          mb="md"
        />

        {uploading && <Loader size="sm" mb="md" />}
        {preview && <Image src={preview} width={200} radius="md" mb="md" />}

        <NumberInput
          label="Порядок"
          value={order}
          onChange={(val) => setOrder(typeof val === 'number' ? val : 0)}
          min={0}
          mb="md"
        />

        <TextInput
          label="Ссылка (опционально)"
          value={link}
          onChange={(e) => setLink(e.currentTarget.value)}
          placeholder="https://example.com"
          mb="md"
        />

        <DateTimePicker
          label="Начало скидки"
          value={discountStart}
          onChange={(value) => setDiscountStart(value ? new Date(value) : null)}
          valueFormat="YYYY-MM-DDTHH:mm:ss"
          clearable
          mb="md"
        />

        <DateTimePicker
          label="Окончание скидки"
          value={discountUntil}
          onChange={(value) => setDiscountUntil(value ? new Date(value) : null)}
          valueFormat="YYYY-MM-DDTHH:mm:ss"
          clearable
          mb="md"
        />

        <Button fullWidth onClick={handleSubmit} disabled={uploading}>
          Сохранить баннер
        </Button>

        {error && (
          <Notification color="red" mt="md" onClose={() => setError(null)}>
            {error}
          </Notification>
        )}
      </Container>
    </Layout>
  );
}
