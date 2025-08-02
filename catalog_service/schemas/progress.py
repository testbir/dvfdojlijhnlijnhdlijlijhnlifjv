# catalog_service/schemas/progress.py



from pydantic import BaseModel
from typing import List


class CourseProgressSchema(BaseModel):
    course_id: int
    course_title: str
    total_modules: int
    completed_modules: int
    progress_percent: float

class SingleCourseProgressSchema(BaseModel):
    course_id: int
    course_title: str
    total_modules: int
    completed_modules: List[int]
    progress_percent: float
