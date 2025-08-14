# learning_service/shemas/block.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class BlockCreate(BaseModel):
    type: str
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    language: Optional[str] = None
    video_preview: Optional[str] = None

class BlockUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    language: Optional[str] = None
    video_preview: Optional[str] = None

class BlockSchema(BaseModel):
    id: int
    module_id: int
    type: str
    title: Optional[str]
    content: Optional[str]
    order: int
    language: Optional[str]
    video_preview: Optional[str]

    model_config = ConfigDict(from_attributes=True)
