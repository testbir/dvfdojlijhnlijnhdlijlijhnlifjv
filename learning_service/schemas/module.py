# learning_service/shemas/module.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class ModuleCreate(BaseModel):
    title: str
    group_title: Optional[str] = None
    order: Optional[int] = None
    sp_award: int = 0
    completion_message: Optional[str] = None

class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    group_title: Optional[str] = None
    order: Optional[int] = None
    sp_award: Optional[int] = None
    completion_message: Optional[str] = None

class ModuleSchema(BaseModel):
    id: int
    course_id: int
    title: str
    group_title: Optional[str]
    order: int
    sp_award: int
    completion_message: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class GroupWithModules(BaseModel):
    group_title: Optional[str]
    modules: List[ModuleSchema]
