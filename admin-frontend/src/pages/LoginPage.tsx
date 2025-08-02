//pages/LoginPage.tsx



import { useState, useContext } from 'react';
import { login as loginApi } from '../api/authApi';
import { AuthContext } from '../context/AuthContext';
import { Container, TextInput, PasswordInput, Button, Title, Notification } from '@mantine/core';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const { login } = useContext(AuthContext);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    try {
      const res = await loginApi(username, password);
      login(res.access_token);
      navigate('/');  // теперь редиректим через роутер
    } catch {
      setError('Неверный логин или пароль');
    }
  };

  return (
    <Container size="xs" mt={50}>
      <Title order={2} ta="center" mb="lg">Вход в админку</Title>

      <TextInput
        label="Логин"
        placeholder="Введите логин"
        value={username}
        onChange={(e) => setUsername(e.currentTarget.value)}
        required
        mb="md"
      />

      <PasswordInput
        label="Пароль"
        placeholder="Введите пароль"
        value={password}
        onChange={(e) => setPassword(e.currentTarget.value)}
        required
        mb="md"
      />

      <Button fullWidth onClick={handleSubmit} mt="xl">
        Войти
      </Button>

      {error && (
        <Notification color="red" mt="md" onClose={() => setError(null)}>
          {error}
        </Notification>
      )}
    </Container>
  );
}
