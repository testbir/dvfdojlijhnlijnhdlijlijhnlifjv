# id_service/schemas/account.py

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from pydantic import FieldValidationInfo
from typing import Optional, List
from datetime import datetime

from core.security import security


class ProfileResponse(BaseModel):
    """User profile response schema"""
    email: str
    username: str
    email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ChangeEmailRequest(BaseModel):
    """Change email request schema"""
    new_email: EmailStr = Field(..., description="New email address")
    password: str = Field(..., description="Current password for verification")
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    @field_validator('new_email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class ChangeEmailResponse(BaseModel):
    """Change email response schema"""
    message: str = "Verification code sent to new email address"


class ConfirmEmailChangeRequest(BaseModel):
    new_email: EmailStr
    code: str = Field(..., pattern=r'^\d{4}$', description="4-digit verification code")
  
    model_config = ConfigDict(str_strip_whitespace=True)
  
    @field_validator('new_email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class ConfirmEmailChangeResponse(BaseModel):
    """Confirm email change response schema"""
    message: str = "Email address updated successfully"


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    old_password: str = Field(..., description="Current password")
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


class ChangePasswordResponse(BaseModel):
    """Change password response schema"""
    message: str = "Password changed successfully"


class DeleteAccountRequest(BaseModel):
    """Delete account request schema"""
    current_password: str
    confirmation: str = Field(..., pattern=r'^DELETE$', description="Type DELETE to confirm")


class DeleteAccountResponse(BaseModel):
    """Delete account response schema"""
    message: str = "Account has been deleted"