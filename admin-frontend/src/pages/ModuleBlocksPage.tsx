// pages/ModuleBlocksPage.tsx

import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { Container, Title, Table, Button, Group, Loader, Center, Notification } from '@mantine/core';
import { blocksApi } from '../services/adminApi';

interface Block {
  id: number;
  type: string;
  order: number;
}

export default function ModuleBlocksPage() {
  const { moduleId } = useParams<{ moduleId: string }>();
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBlocks = async () => {
      try {
        const data = await blocksApi.getModuleBlocks(Number(moduleId));
        setBlocks(data);
      } catch (error) {
        console.error('Ошибка при загрузке блоков', error);
        setError('Ошибка при загрузке блоков');
      } finally {
        setLoading(false);
      }
    };
    if (moduleId) fetchBlocks();
  }, [moduleId]);

  const handleDeleteBlock = async (blockId: number) => {
    if (!window.confirm('Вы уверены, что хотите удалить блок?')) return;

    try {
      await blocksApi.deleteBlock(blockId);
      setBlocks((prev) => prev.filter((b) => b.id !== blockId));
    } catch (error) {
      console.error('Ошибка при удалении блока:', error);
      setError('Ошибка при удалении блока');
    }
  };

  return (
    <Layout>
      <Container>
        <Title order={2} ta="center" mb="lg">Контент-блоки</Title>

        <Group justify="space-between" mb="lg">
          <Button component={Link} to={`/modules/${moduleId}/blocks/create`}>
            Добавить блок
          </Button>
        </Group>

        {error && (
          <Notification color="red" mb="md">
            {error}
          </Notification>
        )}

        {loading ? (
          <Center>
            <Loader />
          </Center>
        ) : (
          <Table withRowBorders withColumnBorders highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Тип</Table.Th>
                <Table.Th>Порядок</Table.Th>
                <Table.Th>Действия</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {blocks.map((block) => (
                <Table.Tr key={block.id}>
                  <Table.Td>{block.type}</Table.Td>
                  <Table.Td>{block.order}</Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      <Button component={Link} to={`/blocks/${block.id}/edit`} size="xs" variant="light">
                        Редактировать
                      </Button>
                      <Button color="red" size="xs" onClick={() => handleDeleteBlock(block.id)}>
                        Удалить
                      </Button>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Container>
    </Layout>
  );
}
