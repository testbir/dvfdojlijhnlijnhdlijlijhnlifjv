
# catalog_service/schemas/block.py



from pydantic import BaseModel
from typing import List, Optional




class ContentBlockSchema(BaseModel):
    id: int  # Уникальный идентификатор блока
    title: Optional[str]  # Заголовок блока (необязательный)
    type: str  # Тип контента (например, 'video', 'text')
    content: str  # Сам контент блока
    order: int  # Порядок отображения внутри модуля
    video_preview: Optional[str] = None

    class Config:
        orm_mode = True  # Поддержка ORM-совместимости
        
        
#  Схема создания блока контента
class ContentBlockCreateSchema(BaseModel):
    type: str  # text, video, code, image
    title: str
    content: str
    order: int
    video_preview: Optional[str] = None
    
    
    

class BlockOrderUpdate(BaseModel):
    block_id: int
    order: int