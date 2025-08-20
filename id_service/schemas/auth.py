# id_service/schemas/auth.py

from pydantic import BaseModel, EmailStr,  ConfigDict
from typing import Optional
from datetime import datetime
from pydantic import field_validator, FieldValidationInfo, Field
from utils.validators import validators
from core.security import security


class RegisterRequest(BaseModel):
    """Registration request schema"""
    username: str = Field(..., min_length=3, max_length=30, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    password_confirm: str = Field(..., description="Password confirmation")
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        valid, error = validators.validate_username(v)
        if not valid:
            raise ValueError(error)
        return v
    
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()
    
    @field_validator('password')
    @classmethod  
    def validate_password(cls, v: str) -> str:
        valid, error = security.validate_password_strength(v)
        if not valid:
            raise ValueError(error)
        return v
    
    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v: str, info: FieldValidationInfo) -> str:
        if info.data.get('password') and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


class RegisterResponse(BaseModel):
    """Registration response schema"""
    user_id: str
    message: str = "Registration successful. Please check your email for verification code."


class VerifyEmailRequest(BaseModel):
    """Email verification request schema"""
    user_id: str = Field(..., description="User ID from registration")
    code: str = Field(..., pattern=r'^\d{4}$', description="4-digit verification code")
    
    model_config = ConfigDict(str_strip_whitespace=True)


class VerifyEmailResponse(BaseModel):
    """Email verification response schema"""
    ok: bool = True
    message: str = "Email verified successfully"
    redirect_to: Optional[str] = None


class LoginPasswordRequest(BaseModel):
    """Password login request schema"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(default=False, description="Extended session duration")
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class LoginPasswordResponse(BaseModel):
    """Password login response schema"""
    ok: bool = True
    message: str = "Login successful"
    redirect_to: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""
    email: EmailStr = Field(..., description="Email address")
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class ForgotPasswordResponse(BaseModel):
    """Forgot password response schema"""
    message: str = "If an account exists with this email, a reset code has been sent"


class VerifyResetRequest(BaseModel):
    """Password reset verification request schema"""
    email: EmailStr = Field(..., description="Email address")
    code: str = Field(..., pattern=r'^\d{4}$', description="4-digit reset code")
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class VerifyResetResponse(BaseModel):
    """Password reset verification response schema"""
    user_id: str
    reset_token: str


class SetNewPasswordRequest(BaseModel):
    """Set new password request schema"""
    user_id: str = Field(..., description="User ID from reset verification")
    reset_token: str = Field(..., description="Reset token from verification")
    new_password: str = Field(..., min_length=8, description="New password")
    new_password_confirm: str = Field(..., description="New password confirmation")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        valid, error = security.validate_password_strength(v)
        if not valid:
            raise ValueError(error)
        return v
    
    @field_validator('new_password_confirm')
    @classmethod
    def passwords_match(cls, v: str, info: FieldValidationInfo) -> str:
        if info.data.get('new_password') and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


class SetNewPasswordResponse(BaseModel):
    """Set new password response schema"""
    message: str = "Password has been reset successfully"