# catalog_service/schemas/module.py

from schemas.block import ContentBlockSchema
from pydantic import BaseModel
from typing import List, Optional


class ModuleSchema(BaseModel):
    id: int  # Уникальный идентификатор модуля
    group_title: Optional[str]  # Название группы модулей (если есть)
    title: str  # Название модуля
    order: int  # Порядок модуля в курсе
    content_blocks: List[ContentBlockSchema]  # Список блоков контента в модуле

    class Config:
        orm_mode = True
        
        
        
class ModuleShortSchema(BaseModel):
    id: int  # Уникальный идентификатор модуля
    group_title: Optional[str]  # Название группы модулей (если есть)
    title: str  # Название модуля
    order: int  # Порядок модуля в курсе

    class Config:
        orm_mode = True




class ModuleContentSchema(BaseModel):
    module_id: int
    title: str
    blocks: List[ContentBlockSchema]
    is_completed: bool

    class Config:
        orm_mode = True
        
        
class ModuleContentBlockSchema(BaseModel):
    type: str
    content: str
    order: int

    class Config:
        orm_mode = True
        
#  Схема создания модуля
class ModuleCreate(BaseModel):
    group_title: Optional[str] = None
    title: str
    order: int