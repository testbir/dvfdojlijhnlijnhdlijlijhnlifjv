# auth_service/accounts/serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate
from .models import CustomUser, EmailConfirmationCode, EmailChangeRequest


# --- Регистрация ---
class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def validate_email(self, value):
        # Нормализуем email к нижнему регистру
        value = value.lower()
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email уже используется")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username уже используется")
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({"password2": "Пароли не совпадают"})
        return data

    def create(self, validated_data):
        # Дополнительная гарантия нормализации
        validated_data['email'] = validated_data['email'].lower()
        return CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password1'],
            is_active=False
        )


# --- Подтверждение кода ---
class VerifyCodeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(min_length=4, max_length=4)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(id=data['user_id'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({'user_id': 'Пользователь не найден'})

        code_obj = EmailConfirmationCode.objects.filter(
            user=user,
            purpose='register',
            created_at__gte=timezone.now() - timedelta(minutes=10)
        ).order_by('-created_at').first()

        if not code_obj or code_obj.code != data['code']:
            raise serializers.ValidationError({'code': 'Неверный или просроченный код'})

        data['user'] = user
        return data


# --- JWT по Email ---
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Добавляем user_id в payload
        token['user_id'] = user.id
        token['email'] = user.email
        token['username'] = user.username
        
        return token


class EmailTokenObtainPairSerializer(CustomTokenObtainPairSerializer):
    username_field = CustomUser.EMAIL_FIELD

    def validate(self, attrs):
        email = attrs.get("email") or attrs.get("username")
        password = attrs.get("password")

        # Нормализуем email для поиска
        email = email.lower() if email else None

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"detail": "Неверные учетные данные"})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Неверные учетные данные"})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Пользователь не активирован"})

        # Важно! Устанавливаем user для родительского класса
        self.user = user
        
        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return data


# --- Запрос на смену email ---
class EmailChangeRequestSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_email = serializers.EmailField()

    def validate(self, attrs):
        user = self.context['request'].user

        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError("Неверный пароль")

        # Нормализуем новый email
        new_email = attrs['new_email'].lower()
        attrs['new_email'] = new_email

        if CustomUser.objects.filter(email=new_email).exists():
            raise serializers.ValidationError("Этот email уже используется")

        attrs['user'] = user
        return attrs


# --- Подтверждение смены email ---
class ConfirmEmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    code = serializers.CharField()

    def validate(self, attrs):
        user = self.context['request'].user

        # Нормализуем email для поиска
        new_email = attrs['new_email'].lower()
        attrs['new_email'] = new_email

        try:
            request_obj = EmailChangeRequest.objects.get(
                user=user,
                new_email=new_email,
                code=attrs['code']
            )
        except EmailChangeRequest.DoesNotExist:
            raise serializers.ValidationError("Неверный код или email")

        attrs['request_obj'] = request_obj
        return attrs