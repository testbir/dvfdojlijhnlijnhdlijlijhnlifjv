# catalog_service/schemas/promo.py


from pydantic import BaseModel, ConfigDict

class PromoCreateSchema(BaseModel):
    image: str
    course_id: int
    order: int = 0

class PromoSchema(PromoCreateSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)
