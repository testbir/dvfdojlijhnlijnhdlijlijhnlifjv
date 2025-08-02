#catalog_service/schemas/banner.py

from pydantic import BaseModel
from typing import List, Optional

class BannerCreateSchema(BaseModel):
    image: str
    order: int = 0

class BannerSchema(BannerCreateSchema):
    id: int

    class Config:
        orm_mode = True


class BannerUpdateSchema(BaseModel):
    image: Optional[str] = None
    order: int
    link: str
