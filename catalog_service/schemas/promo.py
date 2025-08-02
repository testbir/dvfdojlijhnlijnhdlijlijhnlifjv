# catalog_service/schemas/promo.py


from pydantic import BaseModel

class PromoCreateSchema(BaseModel):
    image: str
    course_id: int
    order: int = 0

class PromoSchema(PromoCreateSchema):
    id: int

    class Config:
        orm_mode = True
