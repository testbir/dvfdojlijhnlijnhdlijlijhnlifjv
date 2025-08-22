# id_service/schemas/user.py
from __future__ import annotations

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, FieldValidationInfo

from utils.validators import validators
from core.security import security


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        ok, err = validators.validate_username(v)
        if not ok:
            raise ValueError(err)
        return v


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    email_verified: bool = False

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        ok, err = security.validate_password_strength(v)
        if not ok:
            raise ValueError(err)
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=30)
    email_verified: Optional[bool] = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        return v.lower() if v else v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        ok, err = validators.validate_username(v)
        if not ok:
            raise ValueError(err)
        return v


class UserRead(BaseModel):
    id: str
    email: str
    username: str
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
