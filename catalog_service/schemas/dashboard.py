# catalog_service/schemas/dashboard.py

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class UserCourseSchema(BaseModel):
    """Упрощенная схема курса для dashboard"""
    course_id: int
    course_title: str
    image: Optional[str] = None
    purchased_at: datetime
    progress_percent: float
    is_completed: bool
    
    class Config:
        # Добавить для всех datetime полей
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class UserStatsSchema(BaseModel):
    """Общая статистика пользователя"""
    total_courses: int
    completed_courses: int
    total_progress_percent: float
    total_study_time: Optional[int] = None  # в минутах, если будете трекать

class UserDashboardSchema(BaseModel):
    """Основная схема для dashboard"""
    user_id: int
    stats: UserStatsSchema
    courses: List[UserCourseSchema]

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }