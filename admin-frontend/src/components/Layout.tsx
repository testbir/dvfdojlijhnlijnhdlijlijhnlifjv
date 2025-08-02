// components/Layout.tsx

import { AppShell, Button, Stack, Title, Divider, Text, Burger, Group } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Link, useLocation } from 'react-router-dom';
import type { ReactNode } from 'react';
import {
  IconHome,
  IconUsers,
  IconChartBar,
  IconTicket,
  IconMail,
  IconDatabase,
  IconSettings,
  IconLogout
} from '@tabler/icons-react';

export default function Layout({ children }: { children: ReactNode }) {
  const { logout } = useContext(AuthContext);
  const location = useLocation();
  const [opened, { toggle }] = useDisclosure(true);

  const navItems = [
    { path: '/', label: 'Курсы', icon: IconHome },
    { path: '/users', label: 'Пользователи', icon: IconUsers },
    { path: '/statistics', label: 'Статистика', icon: IconChartBar },
    { path: '/promo-codes', label: 'Промокоды', icon: IconTicket },
    { path: '/email-campaigns', label: 'Email рассылки', icon: IconMail },
    { path: '/backups', label: 'Резервные копии', icon: IconDatabase },
    { path: '/settings', label: 'Настройки', icon: IconSettings },
  ];

  return (
    <AppShell
      padding="md"
      navbar={{
        width: 260,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      header={{ height: 60 }}
    >
      <AppShell.Header p="md" withBorder>
        <Group justify="space-between" h="100%">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <Title order={3}>📚 Admin Panel</Title>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md" withBorder>
        <Stack gap="xs" style={{ flex: 1 }}>
          <Text size="xs" fw={600} c="dimmed" tt="uppercase" mb="xs">
            Основное меню
          </Text>

          {navItems.slice(0, 2).map((item) => {
            const Icon = item.icon;
            return (
              <Button
                key={item.path}
                component={Link}
                to={item.path}
                variant={location.pathname === item.path ? 'filled' : 'light'}
                fullWidth
                justify="flex-start"
                leftSection={<Icon size={18} />}
              >
                {item.label}
              </Button>
            );
          })}

          <Divider my="sm" />

          <Text size="xs" fw={600} c="dimmed" tt="uppercase" mb="xs">
            Маркетинг
          </Text>

          {navItems.slice(2, 5).map((item) => {
            const Icon = item.icon;
            return (
              <Button
                key={item.path}
                component={Link}
                to={item.path}
                variant={location.pathname === item.path ? 'filled' : 'light'}
                fullWidth
                justify="flex-start"
                leftSection={<Icon size={18} />}
              >
                {item.label}
              </Button>
            );
          })}

          <Divider my="sm" />

          <Text size="xs" fw={600} c="dimmed" tt="uppercase" mb="xs">
            Система
          </Text>

          {navItems.slice(5).map((item) => {
            const Icon = item.icon;
            return (
              <Button
                key={item.path}
                component={Link}
                to={item.path}
                variant={location.pathname === item.path ? 'filled' : 'light'}
                fullWidth
                justify="flex-start"
                leftSection={<Icon size={18} />}
              >
                {item.label}
              </Button>
            );
          })}

          <div style={{ flex: 1 }} />

          <Divider my="sm" />

          <Button
            color="red"
            variant="outline"
            fullWidth
            onClick={logout}
            leftSection={<IconLogout size={18} />}
          >
            Выйти
          </Button>
        </Stack>
      </AppShell.Navbar>

      <AppShell.Main>
        {children}
      </AppShell.Main>
    </AppShell>
  );
}
