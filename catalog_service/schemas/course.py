# catalog_service/schemas/course.py

from pydantic import BaseModel, ConfigDict, field_validator, ValidationInfo
from typing import Optional
from datetime import datetime



class CourseListSchema(BaseModel):
    id: int
    title: str
    short_description: str
    image: Optional[str]
    is_free: bool
    price: float
    discount: float
    final_price: float
    has_access: bool
    button_text: str
    
    group_title: Optional[str] = None
    
    order: Optional[int] = 0
    
    
    discount_start: Optional[datetime] = None
    discount_until: Optional[datetime] = None
    discount_ends_in: Optional[float] = None
    is_discount_active: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class CourseDetailSchema(BaseModel):
    id: int
    title: str
    full_description: Optional[str]
    short_description: Optional[str]
    image: Optional[str]
    is_free: bool
    price: float
    discount: float
    final_price: float
    has_access: bool
    button_text: str

    video: Optional[str] = None
    video_preview: Optional[str] = None
    banner_text: Optional[str] = None
    banner_color_left: Optional[str] = None
    banner_color_right: Optional[str] = None
    
    group_title: Optional[str] = None

    discount_start: Optional[datetime] = None # начало скидки
    discount_until: Optional[datetime] = None # конец скидки
    discount_ends_in: Optional[float] = None
    is_discount_active: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)




class CourseAccessSchema(BaseModel):
    has_access: bool
    reason: str 
    

class BuyCourseResponse(BaseModel):
    success: bool
    message: str


class BuyCourseRequest(BaseModel):
    payment_id: Optional[str] = None



class CourseBuyRequest(BaseModel):
    payment_id: Optional[str] = None  # пока не обрабатываем, но пригодится



class CourseAccessResponse(BaseModel):
    has_access: bool
    reason: str


#  Схема создания курса
class CourseCreate(BaseModel):
    title: str
    short_description: Optional[str] = ""
    full_description: Optional[str] = None
    image: Optional[str] = None
    is_free: bool = False
    price: Optional[float] = None
    discount: Optional[float] = 0.0

    video: Optional[str] = None
    video_preview: Optional[str] = None
    banner_text: Optional[str] = None
    banner_color_left: Optional[str] = None
    banner_color_right: Optional[str] = None
    order: int = 0
    group_title: Optional[str] = None

    discount_start: Optional[datetime] = None
    discount_until: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("price")
    @classmethod
    def validate_price(cls, v, info: ValidationInfo):
        # В Pydantic v2 используем info.data для получения других полей
        if info.data.get("is_free") is False and v is None:
            raise ValueError("Цена обязательна для платного курса")
        return v

    @field_validator("discount_until")
    @classmethod
    def validate_discount_range(cls, v, info: ValidationInfo):
        discount_start = info.data.get("discount_start")
        if discount_start and v and v <= discount_start:
            raise ValueError("Окончание скидки не может быть раньше начала")
        return v