// pages/ModuleEditPage.tsx

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { Container, Title, TextInput, NumberInput, Button, Loader, Center, Notification } from '@mantine/core';
import { modulesApi } from '../services/adminApi';

interface Module {
  id: number;
  title: string;
  group_title: string | null;
  order: number;
}

export default function ModuleEditPage() {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();

  const [module, setModule] = useState<Module | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchModule = async () => {
      try {
        const data = await modulesApi.getModule(Number(moduleId));
        setModule(data);
      } catch (e) {
        setError('Ошибка при загрузке модуля');
      } finally {
        setLoading(false);
      }
    };
    if (moduleId) fetchModule();
  }, [moduleId]);

  const handleSave = async () => {
    if (!moduleId || !module) return;
    setSaving(true);
    try {
      await modulesApi.updateModule(Number(moduleId), {
        title: module.title,
        group_title: module.group_title,
        order: module.order,
      });
      navigate(-1);
    } catch (err) {
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

  if (error) {
    return (
      <Layout>
        <Notification color="red">{error}</Notification>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container size="sm">
        <Title order={2} ta="center" mb="lg">Редактирование модуля</Title>

        <TextInput
          label="Название"
          value={module?.title || ''}
          onChange={(e) => setModule({ ...module!, title: e.currentTarget.value })}
          mb="md"
        />

        <TextInput
          label="Группа"
          value={module?.group_title || ''}
          onChange={(e) => setModule({ ...module!, group_title: e.currentTarget.value })}
          mb="md"
        />

        <NumberInput
          label="Порядок"
          value={module?.order ?? 1}
          onChange={(val) => setModule({ ...module!, order: (typeof val === 'number' ? val : 1) as number })}
          mb="md"
        />

        <Button fullWidth onClick={handleSave} loading={saving}>
          Сохранить
        </Button>
      </Container>
    </Layout>
  );
}
