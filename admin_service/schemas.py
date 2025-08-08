# admin_service/schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Создание курса
class CourseCreate(BaseModel):
    title: str
    short_description: Optional[str] = ""
    full_description: Optional[str] = ""
    image: Optional[str] = None
    is_free: bool = False
    price: Optional[float] = None
    discount: Optional[float] = 0.0
    video: Optional[str] = None
    video_preview: Optional[str] = None
    banner_text: Optional[str] = None
    banner_color_left: Optional[str] = None
    banner_color_right: Optional[str] = None
    group_title: Optional[str] = None
    order: int = 0
    discount_start: Optional[datetime] = None
    discount_until: Optional[datetime] = None
    

# Создание модуля
class ModuleCreate(BaseModel):
    group_title: Optional[str]
    title: str
    order: int

# Контент-блок
class ContentBlockCreate(BaseModel):
    type: str  # text, video, code, image
    title: str
    content: str
    order: int
    video_preview: Optional[str] = None
    language: Optional[str] = None  # Новое поле для языка программирования


class AdminLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BlockOrderUpdateSchema(BaseModel):
    block_id: int
    order: int
    
    
class BannerCreate(BaseModel):
    image: str
    order: int = 0
    link: str

class PromoCreate(BaseModel):
    image: str
    course_id: int
    order: int = 0
