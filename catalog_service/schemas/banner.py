#catalog_service/schemas/banner.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class BannerCreateSchema(BaseModel):
    image: str
    order: int = 0
    link: Optional[str] = ""

class BannerSchema(BannerCreateSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BannerUpdateSchema(BaseModel):
    image: Optional[str] = None
    order: Optional[int] = None
    link: Optional[str] = None
