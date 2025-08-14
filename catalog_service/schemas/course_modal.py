# catalog_service/schemas/course_modal.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional



class CourseModalBlockCreate(BaseModel):
    type: str  # 'text' или 'image'
    content: str
    order: int = 0

class CourseModalBlockSchema(BaseModel):
    id: int
    type: str
    content: str
    order: int

    model_config = ConfigDict(from_attributes=True)
    
        

class CourseModalCreate(BaseModel):
    title: str
    blocks: List[CourseModalBlockCreate] = []

class CourseModalUpdate(BaseModel):
    title: Optional[str] = None
    blocks: Optional[List[CourseModalBlockCreate]] = None

class CourseModalSchema(BaseModel):
    id: int
    course_id: int
    title: str
    blocks: List[CourseModalBlockSchema]
    
    model_config = ConfigDict(from_attributes=True)
