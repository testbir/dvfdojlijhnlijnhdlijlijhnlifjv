# catalog_service/schemas/student_works.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class StudentWorkCreate(BaseModel):
    image: str
    description: Optional[str] = None
    bot_tag: Optional[str] = None
    order: int = 0

class StudentWorkSchema(BaseModel):
    id: int
    image: str
    description: Optional[str]
    bot_tag: Optional[str]
    order: int
    
    model_config = ConfigDict(from_attributes=True)


class StudentWorksSectionCreate(BaseModel):
    title: str
    description: str
    works: List[StudentWorkCreate] = []

class StudentWorksSectionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    works: Optional[List[StudentWorkCreate]] = None

class StudentWorksSectionSchema(BaseModel):
    id: int
    course_id: int
    title: str
    description: str
    works: List[StudentWorkSchema]

    model_config = ConfigDict(from_attributes=True) 
