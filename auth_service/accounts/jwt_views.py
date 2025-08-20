# auth_service/accounts/jwt_views.py


from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import EmailTokenObtainPairSerializer
from .throttles import LoginIPThrottle
from .models import CustomUser

@extend_schema(
    summary="Получение JWT токенов (вход)",
    description="Принимает username и пароль, возвращает access и refresh токены.",
    request=TokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(description="Успешный вход и получение токенов"),
        400: OpenApiResponse(description="Пользователь не активирован"),
        401: OpenApiResponse(description="Неверные учетные данные"),
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginIPThrottle]
    serializer_class = EmailTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        # Получаем email из запроса
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'invalid_credentials',
                'message': 'Email и пароль обязательны'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Проверяем пароль
            if not user.check_password(password):
                return Response({
                    'error': 'invalid_credentials', 
                    'message': 'Неверные учетные данные'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем активацию ПОСЛЕ проверки пароля
            if not user.is_active or not user.is_email_confirmed:
                return Response({
                    'error': 'account_not_activated',
                    'message': 'Пользователь не активирован',
                    'user_id': user.id,
                    'email': user.email
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'invalid_credentials',
                'message': 'Неверные учетные данные' 
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Если все проверки прошли - продолжаем стандартную логику
        return super().post(request, *args, **kwargs)

@extend_schema(
    summary="Обновление access-токена",
    description="Принимает refresh-токен и возвращает новый access-токен.",
    request=TokenRefreshSerializer,
    responses={
        200: OpenApiResponse(description="Новый access-токен получен"),
        401: OpenApiResponse(description="Недействительный или просроченный refresh-токен"),
    }
)
class CustomTokenRefreshView(TokenRefreshView):
    pass