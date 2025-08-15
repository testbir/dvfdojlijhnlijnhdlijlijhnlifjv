# learning_service/schemas/module.py

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

class ModuleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    group_title: Optional[str] = Field(default=None, max_length=255)
    order: Optional[int] = Field(default=None, ge=1)
    sp_award: int = Field(default=0, ge=0)
    completion_message: Optional[str] = None
    model_config = ConfigDict(extra="forbid")
    
class ModuleUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    group_title: Optional[str] = Field(default=None, max_length=255)
    order: Optional[int] = Field(default=None, ge=1)
    sp_award: Optional[int] = Field(default=None, ge=0)
    completion_message: Optional[str] = None
    model_config = ConfigDict(extra="forbid")
    
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
