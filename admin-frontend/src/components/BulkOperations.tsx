// src/components/BulkOperations.tsx

import { useState } from 'react';
import {
  Modal,
  Button,
  Group,
  Stack,
  Alert,
  Select,
} from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';
import axios from '../api/axiosInstance';

interface BulkOperationsProps {
  selectedItems: number[];
  itemType: 'courses' | 'modules' | 'blocks' | 'users';
  onComplete: () => void;
}

export function BulkOperations({ selectedItems, itemType, onComplete }: BulkOperationsProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [operation, setOperation] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const operations = {
    courses: [
      { value: 'delete', label: 'Удалить выбранные курсы' },
      { value: 'toggle_free', label: 'Сделать бесплатными/платными' },
      { value: 'apply_discount', label: 'Применить скидку' },
      { value: 'reorder', label: 'Изменить порядок' },
    ],
    modules: [
      { value: 'delete', label: 'Удалить выбранные модули' },
      { value: 'move', label: 'Переместить в другой курс' },
      { value: 'duplicate', label: 'Дублировать модули' },
    ],
    blocks: [
      { value: 'delete', label: 'Удалить выбранные блоки' },
      { value: 'change_type', label: 'Изменить тип блоков' },
      { value: 'reorder', label: 'Изменить порядок' },
    ],
    users: [
      { value: 'activate', label: 'Активировать пользователей' },
      { value: 'deactivate', label: 'Деактивировать пользователей' },
      { value: 'grant_course', label: 'Предоставить доступ к курсу' },
      { value: 'send_email', label: 'Отправить email' },
    ],
  };

  const handleExecute = async () => {
    if (!operation || selectedItems.length === 0) return;

    setLoading(true);
    try {
      await axios.post(`/admin/bulk-operations/${itemType}/`, {
        operation,
        ids: selectedItems,
      });
      
      setModalOpen(false);
      onComplete();
    } catch (error) {
      console.error('Ошибка массовой операции:', error);
    } finally {
      setLoading(false);
    }
  };

  if (selectedItems.length === 0) return null;

  return (
    <>
      <Button
        onClick={() => setModalOpen(true)}
        variant="outline"
      >
        Массовые операции ({selectedItems.length})
      </Button>

      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Массовые операции"
        size="md"
      >
        <Stack>
          <Alert icon={<IconAlertCircle size={16} />} color="yellow">
            Выбрано элементов: {selectedItems.length}
          </Alert>

          <Select
            label="Выберите операцию"
            placeholder="Выберите действие"
            data={operations[itemType]}
            value={operation}
            onChange={(val) => setOperation(val || '')}
          />

          {operation === 'apply_discount' && (
            <Select
              label="Размер скидки"
              data={[
                { value: '10', label: '10%' },
                { value: '20', label: '20%' },
                { value: '30', label: '30%' },
                { value: '50', label: '50%' },
              ]}
            />
          )}

          {operation === 'grant_course' && (
            <Select
              label="Выберите курс"
              placeholder="Курс для предоставления доступа"
              data={[]} // Здесь должен быть список курсов
            />
          )}

          <Group justify="flex-end" mt="md">
            <Button variant="light" onClick={() => setModalOpen(false)}>
              Отмена
            </Button>
            <Button
              color="red"
              onClick={handleExecute}
              loading={loading}
              disabled={!operation}
            >
              Выполнить
            </Button>
          </Group>
        </Stack>
      </Modal>
    </>
  );
}