# catalog_service/schemas/learning.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class GroupResponse(BaseModel):
    id: str
    title: str
    order: int
    
    class Config:
        orm_mode = True


class ModuleResponse(BaseModel):
    id: str
    title: str
    groupId: str
    order: int
    
    class Config:
        orm_mode = True


class ContentBlockResponse(BaseModel):
    id: str
    type: str  # 'text' | 'code' | 'video' | 'image'
    title: str
    content: str
    order: int
    
    class Config:
        orm_mode = True


class CourseDataResponse(BaseModel):
    id: str
    title: str
    groups: List[GroupResponse]
    modules: List[ModuleResponse]
    progress: float
    
    class Config:
        orm_mode = True


class ModuleProgressResponse(BaseModel):
    moduleId: str
    isCompleted: bool
    completedAt: Optional[datetime]
    
    class Config:
        orm_mode = True


class UpdatePositionRequest(BaseModel):
    moduleId: str
    position: int


class CourseAccessResponse(BaseModel):
    hasAccess: bool
    
    class Config:
        orm_mode = True