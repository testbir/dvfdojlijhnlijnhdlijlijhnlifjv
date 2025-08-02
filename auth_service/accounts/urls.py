# auth_service/accounts/urls.py

from django.urls import path

from accounts.jwt_views import (CustomTokenObtainPairView, 
                                CustomTokenRefreshView,
                                CustomTokenObtainPairView, 
                                CustomTokenRefreshView)


from .api import (protected_view, 
                  logout_view, 
                  resend_code,
                  get_user_data,)

from .api import (
    RequestResetPasswordAPIView,
    VerifyResetCodeAPIView,
    SetNewPasswordAPIView,
    VerifyCodeAPIView,
    RegisterAPIView,
    RequestEmailChangeAPIView, 
    ConfirmEmailChangeAPIView,
)

urlpatterns = [
    path('api/register/', RegisterAPIView.as_view(), name='api_register'), # Регистрация
    path('api/verify-code/', VerifyCodeAPIView.as_view(), name='api_verify_code'), # Подтверждение Email по коду
    path('api/protected/', protected_view, name='protected'), # Проверка авторизации
    path('api/logout/', logout_view, name='api_logout'), # Выход с инвалидом refresh-токеном
    path('api/request-reset/', RequestResetPasswordAPIView.as_view(), name='request_reset'), # Ещё не добавлен 
    path('api/verify-reset-code/', VerifyResetCodeAPIView.as_view(), name='verify_reset_code'), # Подтверждение сброса кода
    path('api/set-new-password/', SetNewPasswordAPIView.as_view(), name='set_new_password'), # Установка нового пароля
    path('api/resend-code/', resend_code, name='resend_code'),
    path('api/user/', get_user_data, name='api_user_data'),
]


urlpatterns += [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]


urlpatterns += [
    path('api/request-email-change/', RequestEmailChangeAPIView.as_view(), name='request_email_change'),
    path('api/confirm-email-change/', ConfirmEmailChangeAPIView.as_view(), name='confirm_email_change'),
]
