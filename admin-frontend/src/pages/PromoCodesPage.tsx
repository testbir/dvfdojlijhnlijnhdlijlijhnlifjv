// src/pages/PromoCodesPage.tsx

import { useEffect, useState } from 'react';
import {
  Form,
  Input,
  InputNumber,
  DatePicker,
  Table,
  Button,
  Space,
  Popconfirm,
  message,
  Tag,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import axiosInstance from '../api/axiosInstance';

const { RangePicker } = DatePicker;

interface PromoCode {
  id: number;
  code: string;
  discount_percent?: number;
  discount_amount?: number;
  uses_left: number;
  max_uses: number;
  valid_from: string;
  valid_until: string;
}

interface PromoFormValues {
  code: string;
  discount_percent?: number;
  discount_amount?: number;
  max_uses: number;
  valid_range: [dayjs.Dayjs, dayjs.Dayjs];
}

export default function PromoCodesPage() {
  const [form] = Form.useForm<PromoFormValues>();
  const [promoCodes, setPromoCodes] = useState<PromoCode[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPromoCodes();
  }, []);

  const fetchPromoCodes = async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get<PromoCode[]>('/admin/promocodes/');
      setPromoCodes(response.data);
    } catch {
      message.error('Ошибка при загрузке промокодов');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await axiosInstance.delete(`/admin/promocodes/${id}/`);
      message.success('Промокод удалён');
      fetchPromoCodes();
    } catch {
      message.error('Ошибка при удалении');
    }
  };

  const handleSubmit = async (values: PromoFormValues) => {
    if (
      (!values.discount_percent && !values.discount_amount) ||
      (values.discount_percent && values.discount_amount)
    ) {
      return message.error('Укажите только одну скидку: % или сумму');
    }

    const payload = {
      ...values,
      valid_from: values.valid_range[0].toISOString(),
      valid_until: values.valid_range[1].toISOString(),
    };

    try {
      if (editingId) {
        await axiosInstance.put(`/admin/promocodes/${editingId}/`, payload);
        message.success('Промокод обновлён');
      } else {
        await axiosInstance.post('/admin/promocodes/', payload);
        message.success('Промокод создан');
      }
      form.resetFields();
      setEditingId(null);
      fetchPromoCodes();
    } catch {
      message.error('Ошибка при сохранении');
    }
  };

  const handleEdit = (promo: PromoCode) => {
    setEditingId(promo.id);
    form.setFieldsValue({
      code: promo.code,
      discount_percent: promo.discount_percent,
      discount_amount: promo.discount_amount,
      max_uses: promo.max_uses,
      valid_range: [dayjs(promo.valid_from), dayjs(promo.valid_until)],
    });
  };

  const columns: ColumnsType<PromoCode> = [
    {
      title: 'Код',
      dataIndex: 'code',
    },
    {
      title: 'Скидка',
      render: (_, record) =>
        record.discount_percent
          ? `${record.discount_percent}%`
          : `${record.discount_amount}₽`,
    },
    {
      title: 'Осталось использований',
      render: (r) => `${r.uses_left} / ${r.max_uses}`,
    },
    {
      title: 'Срок действия',
      render: (r) =>
        `${dayjs(r.valid_from).format('DD.MM.YY HH:mm')} — ${dayjs(r.valid_until).format(
          'DD.MM.YY HH:mm'
        )}`,
    },
    {
      title: 'Статус',
      render: (r) => {
        const now = dayjs();
        const start = dayjs(r.valid_from);
        const end = dayjs(r.valid_until);
        let status: 'Ожидается' | 'Активен' | 'Истёк' | 'Исчерпан';

        if (r.uses_left === 0) status = 'Исчерпан';
        else if (now.isBefore(start)) status = 'Ожидается';
        else if (now.isAfter(end)) status = 'Истёк';
        else status = 'Активен';

        const color = {
          Активен: 'green',
          Ожидается: 'blue',
          Истёк: 'red',
          Исчерпан: 'orange',
        }[status];

        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: 'Действия',
      render: (r) => (
        <Space>
          <Button onClick={() => handleEdit(r)} size="small">
            Изменить
          </Button>
          <Popconfirm title="Удалить промокод?" onConfirm={() => handleDelete(r.id)}>
            <Button danger size="small">
              Удалить
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Form
        layout="vertical"
        form={form}
        onFinish={handleSubmit}
        style={{ marginBottom: 24, maxWidth: 600 }}
      >
        <Space style={{ justifyContent: 'space-between', width: '100%' }}>
          <h2>{editingId ? 'Редактировать промокод' : 'Создать промокод'}</h2>
          {editingId && (
            <Button
              onClick={() => {
                form.resetFields();
                setEditingId(null);
              }}
            >
              Отмена
            </Button>
          )}
        </Space>

        <Form.Item name="code" label="Код" rules={[{ required: true, message: 'Введите код' }]}>
          <Input />
        </Form.Item>

        <Form.Item name="discount_percent" label="Скидка (%)">
          <InputNumber min={1} max={100} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item name="discount_amount" label="Скидка (₽)">
          <InputNumber min={1} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="max_uses"
          label="Максимум использований"
          rules={[{ required: true, message: 'Введите максимум использований' }]}
        >
          <InputNumber min={1} style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="valid_range"
          label="Срок действия"
          rules={[{ required: true, message: 'Выберите диапазон' }]}
        >
          <RangePicker showTime format="DD.MM.YY HH:mm" style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" block>
            {editingId ? 'Сохранить' : 'Создать'}
          </Button>
        </Form.Item>
      </Form>

      <Table
        dataSource={promoCodes}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
}
