# learning_service/shemas/progress.py

from pydantic import BaseModel
from typing import List, Optional

class CourseProgressResponse(BaseModel):
    course_id: int
    total_modules: int
    completed_modules: int
    progress_percent: float
    current_position: Optional[int] = None  # 1-based индекс текущего модуля

class CompleteModuleResponse(BaseModel):
    success: bool
    awarded_sp: int
    already_completed: bool
    completion_message: Optional[str] = None
