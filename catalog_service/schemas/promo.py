# catalog_service/schemas/promo.py


from pydantic import BaseModel, ConfigDict
from typing import Optional

class PromoCreateSchema(BaseModel):
    image: str
    course_id: int
    order: int = 0

class PromoSchema(PromoCreateSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)



class PromoUpdateSchema(BaseModel):
    image: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    course_id: Optional[int] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None
