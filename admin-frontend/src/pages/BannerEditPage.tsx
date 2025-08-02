// src/pages/BannerEditPage.tsx

import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from '../api/axiosInstance';
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

    axios
      .get('/admin/banners/')
      .then((res) => {
        const banner = res.data.find((b: any) => b.id === Number(id));
        if (banner) {
          setImage(banner.image);
          setOrder(banner.order);
          setLink(banner.link || '');
        setDiscountStart(banner.discount_start ? new Date(banner.discount_start) : null);
        setDiscountUntil(banner.discount_until ? new Date(banner.discount_until) : null);

        } else {
          setError('Баннер не найден');
        }
      })
      .catch(() => {
        setError('Ошибка загрузки баннера');
      });
  }, [id]);

 const handleSave = async () => {
  if (!id) {
    setError('ID баннера не определён');
    return;
  }

  try {
    setLoading(true);
    const form = new FormData(); // <- сначала создаём form
    form.append('order', order.toString());
    form.append('link', link);

    if (file) {
      form.append('file', file);
    }

    // Только теперь добавляем скидки
    if (discountStart) {
      form.append('discount_start', discountStart.toISOString());
    }
    if (discountUntil) {
      form.append('discount_until', discountUntil.toISOString());
    }

    await axios.put(`/admin/banners/${id}`, form, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

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
