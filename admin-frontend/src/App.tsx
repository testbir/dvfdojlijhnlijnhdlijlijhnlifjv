// src/App.tsx


import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AppRouter from './router/AppRouter';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import theme from './theme';

export default function App() {
  return (
    <MantineProvider theme={theme} defaultColorScheme="light">
      <Notifications />
      <AuthProvider>
        <BrowserRouter>
          <AppRouter />
        </BrowserRouter>
      </AuthProvider>
    </MantineProvider>
  );
}
