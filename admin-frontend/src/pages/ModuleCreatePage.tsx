//pages/ModuleCreatePage.tsx




import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../api/axiosInstance';
import Layout from '../components/Layout';
import {
  Container,
  Title,
  TextInput,
  Button,
  NumberInput,
  Notification,
} from '@mantine/core';

export default function ModuleCreatePage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [groupTitle, setGroupTitle] = useState('');
  const [order, setOrder] = useState<number>(1);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    try {
      await axios.post(`/admin/courses/${courseId}/modules/`, {
        title,
        group_title: groupTitle || null,
        order: order,
      });
      navigate(`/courses/${courseId}`);
    } catch (err) {
      console.error(err);
      setError('Ошибка при создании модуля');
    }
  };

  return (
    <Layout>
      <Container>
        <Title order={2} ta="center" mb="lg">
          Создание модуля
        </Title>

        <TextInput
          label="Название модуля"
          value={title}
          onChange={(e) => setTitle(e.currentTarget.value)}
          mb="md"
        />

        <TextInput
          label="Группа (опционально)"
          value={groupTitle}
          onChange={(e) => setGroupTitle(e.currentTarget.value)}
          mb="md"
        />

        <NumberInput
          label="Порядок"
          value={order}
          onChange={(val) => {
            if (typeof val === 'number') {
              setOrder(val);
            } else {
              setOrder(1);
            }
          }}
          min={1}
          mb="md"
        />

        <Button fullWidth mt="lg" onClick={handleSubmit}>
          Создать модуль
        </Button>

        {error && (
          <Notification color="red" mt="md">
            {error}
          </Notification>
        )}
      </Container>
    </Layout>
  );
}
