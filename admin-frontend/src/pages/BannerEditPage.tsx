// src/pages/BannerEditPage.tsx

import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Layout from '../components/Layout';
import { DateTimePicker } from '@mantine/dates';
import {
  Container,
  Title,
  FileInput,
  NumberInput,
  Button,
  Notification,
  Image,
  TextInput,
  Loader,
} from '@mantine/core';
import { bannersApi } from '../services/adminApi';

export default function BannerEditPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState<number>(0);
  const [link, setLink] = useState<string>('');
  const [image, setImage] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [discountStart, setDiscountStart] = useState<Date | null>(null);
  const [discountUntil, setDiscountUntil] = useState<Date | null>(null);

  useEffect(() => {
    if (!id) {
      setError('Некорректный ID баннера');
      return;
    }

    (async () => {
      try {
        const banner = await bannersApi.getBanner(Number(id));
        setImage(banner.image);
        setOrder(banner.order ?? 0);
        setLink(banner.link || '');
        setDiscountStart(banner.discount_start ? new Date(banner.discount_start) : null);
        setDiscountUntil(banner.discount_until ? new Date(banner.discount_until) : null);
      } catch {
        setError('Ошибка загрузки баннера');
      }
    })();
  }, [id]);

  const handleSave = async () => {
    if (!id) {
      setError('ID баннера не определён');
      return;
    }

    try {
      setLoading(true);
      const form = new FormData();
      form.append('order', order.toString());
      form.append('link', link);
      if (file) form.append('file', file);
      if (discountStart) form.append('discount_start', discountStart.toISOString());
      if (discountUntil) form.append('discount_until', discountUntil.toISOString());

      await bannersApi.updateBanner(Number(id), form);
      navigate('/');
    } catch {
      setError('Ошибка при сохранении');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Container size="sm">
        <Title order={2} ta="center" mb="lg">
          Редактировать баннер
        </Title>

        {error && (
          <Notification color="red" mt="md">
            {error}
          </Notification>
        )}

        {!error && (
          <>
            {image && <Image src={image} width={200} radius="md" mb="md" />}

            <FileInput
              label="Новое изображение (необязательно)"
              accept="image/*"
              onChange={(f) => setFile(f)}
              mb="md"
            />

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
              mb="md"
            />

            <DateTimePicker
              label="Начало скидки"
              value={discountStart}
              onChange={(val) => setDiscountStart(val ? new Date(val) : null)}
              valueFormat="YYYY-MM-DDTHH:mm:ss"
              clearable
              mb="md"
            />

            <DateTimePicker
              label="Окончание скидки"
              value={discountUntil}
              onChange={(val) => setDiscountUntil(val ? new Date(val) : null)}
              valueFormat="YYYY-MM-DDTHH:mm:ss"
              clearable
              mb="md"
            />

            <Button fullWidth onClick={handleSave} disabled={loading}>
              Сохранить
            </Button>

            {loading && <Loader mt="md" />}
          </>
        )}
      </Container>
    </Layout>
  );
}
