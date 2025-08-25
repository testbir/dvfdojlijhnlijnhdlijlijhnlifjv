# id_service/schemas/auth.py
"""
Схемы (Pydantic v2) для auth-флоу.
Важно:
- Все ручки, кроме /oidc/token и /oidc/revoke, работают в JSON.
- Здесь описываем только структуры запросов/ответов и валидацию полей.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from pydantic import field_validator, FieldValidationInfo, Field

from utils.validators import validators
from core.security import security


# ---------------------------
# Регистрация
# ---------------------------

class RegisterRequest(BaseModel):
    """Запрос на регистрацию."""
    username: str = Field(..., min_length=3, max_length=30, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    password_confirm: str = Field(..., description="Password confirmation")

    # Общие настройки модели
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        ok, err = validators.validate_username(v)
        if not ok:
            raise ValueError(err)
        return v

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        ok, err = security.validate_password_strength(v)
        if not ok:
            raise ValueError(err)
        return v

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v: str, info: FieldValidationInfo) -> str:
        if info.data.get('password') and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v
    

class RegisterResponse(BaseModel):
    """Ответ на регистрацию."""
    user_id: str
    email: EmailStr
    requires_verification: bool = True
    message: str = "Registration successful. Please check your email for verification code."
    
# ---------------------------
# Подтверждение e-mail (OTP)
# ---------------------------

class VerifyEmailRequest(BaseModel):
    """Подтверждение e-mail по OTP-коду.
    Дополнительно поддерживает state для завершения pending /authorize.
    """
    user_id: str = Field(..., description="User ID from registration")
    code: str = Field(..., pattern=r'^\d{4}$', description="4-digit verification code")
    state: Optional[str] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class VerifyEmailResponse(BaseModel):
    """Ответ на верификацию e-mail."""
    ok: bool = True
    message: str = "Email verified successfully"
    redirect_to: Optional[str] = None  # для SPA-редиректа без 302


# ---------------------------
# Логин по паролю (JSON-only)
# ---------------------------

class LoginPasswordRequest(BaseModel):
    """Запрос логина по паролю.
    JSON-only. Формы не используются.
    Если переданы client_id+state и в Redis есть pending authreq — вернём redirect_to.
    """
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(default=False, description="Extended session duration")
    # Дополнительно для OIDC продолжения (опционально):
    client_id: Optional[str] = Field(default=None, description="OIDC client_id for pending /authorize")
    state: Optional[str] = Field(default=None, description="State from pending /authorize")

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class LoginPasswordResponse(BaseModel):
    """Ответ на логин по паролю."""
    ok: bool = True
    message: str = "Login successful"
    redirect_to: Optional[str] = None  # SPA-редирект без 302, либо null


# ---------------------------
# Сброс пароля (OTP → reset_token)
# ---------------------------

class ForgotPasswordRequest(BaseModel):
    """Запрос на отправку кода для сброса пароля."""
    email: EmailStr = Field(..., description="Email address")

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class ForgotPasswordResponse(BaseModel):
    """Ответ на запрос сброса пароля.
    Текст одинаковый, чтобы не раскрывать наличие аккаунта.
    """
    message: str = "If an account exists with this email, a reset code has been sent"


class VerifyResetRequest(BaseModel):
    """Подтверждение кода для сброса пароля."""
    email: EmailStr = Field(..., description="Email address")
    code: str = Field(..., pattern=r'^\d{4}$', description="4-digit reset code")

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class VerifyResetResponse(BaseModel):
    """Ответ с reset_token для установки нового пароля."""
    user_id: str
    reset_token: str


class SetNewPasswordRequest(BaseModel):
    """Установка нового пароля после успешной верификации сброса."""
    user_id: str = Field(..., description="User ID from reset verification")
    reset_token: str = Field(..., description="Reset token from verification")
    new_password: str = Field(..., min_length=8, description="New password")
    new_password_confirm: str = Field(..., description="New password confirmation")

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        ok, err = security.validate_password_strength(v)
        if not ok:
            raise ValueError(err)
        return v

    @field_validator('new_password_confirm')
    @classmethod
    def passwords_match(cls, v: str, info: FieldValidationInfo) -> str:
        if info.data.get('new_password') and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


class SetNewPasswordResponse(BaseModel):
    """Ответ на успешную установку нового пароля."""
    message: str = "Password has been reset successfully"
