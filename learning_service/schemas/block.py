# learning_service/schemas/block.py


from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Literal

class BlockCreate(BaseModel):
    type: Literal["text", "image", "video", "code"]
    title: Optional[str] = Field(default=None, min_length=1)
    content: Optional[str] = None
    order: Optional[int] = Field(default=None, ge=1)
    language: Optional[str] = Field(default=None, max_length=50)
    video_preview: Optional[str] = None
    model_config = ConfigDict(extra="forbid")

    @field_validator("content")
    @classmethod
    def content_rules(cls, v, info):
        t = info.data.get("type")
        if t == "text" and not v:
            raise ValueError("content обязателен для text")
        return v

class BlockUpdate(BaseModel):
    type: Optional[Literal["text", "image", "video", "code"]] = None
    title: Optional[str] = Field(default=None, min_length=1)
    content: Optional[str] = None
    order: Optional[int] = Field(default=None, ge=1)
    language: Optional[str] = Field(default=None, max_length=50)
    video_preview: Optional[str] = None
    model_config = ConfigDict(extra="forbid")

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