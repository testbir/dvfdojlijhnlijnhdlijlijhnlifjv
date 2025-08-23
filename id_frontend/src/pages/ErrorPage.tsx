// ============= src/pages/ErrorPage.tsx =============

import React from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Layout } from '../components/Layout/Layout';
import { ROUTES } from '../utils/constants';
import '../styles/pages.scss';

export const ErrorPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  
  const error = searchParams.get('error');
  const description = searchParams.get('description');

  const getErrorMessage = (): { title: string; message: string } => {
    switch (error) {
      case 'invalid_request':
        return {
          title: 'Неверный запрос',
          message: description || 'Запрос содержит недопустимые параметры',
        };
      case 'unauthorized_client':
        return {
          title: 'Неавторизованный клиент',
          message: description || 'Клиент не авторизован для выполнения этого запроса',
        };
      case 'access_denied':
        return {
          title: 'Доступ запрещен',
          message: description || 'Вы отклонили запрос на авторизацию',
        };
      case 'server_error':
        return {
          title: 'Ошибка сервера',
          message: description || 'Произошла внутренняя ошибка сервера',
        };
      default:
        return {
          title: 'Ошибка',
          message: description || 'Произошла неизвестная ошибка',
        };
    }
  };

  const { title, message } = getErrorMessage();

  return (
    <Layout>
      <div className="error-page">
        <div className="error-page__content">
          <h1 className="error-page__title">{title}</h1>
          <p className="error-page__message">{message}</p>
          <Link to={ROUTES.HOME} className="error-page__link">
            Вернуться на главную
          </Link>
        </div>
      </div>
    </Layout>
  );
};