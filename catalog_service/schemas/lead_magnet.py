# catalog_service/schemas/lead_magnet.py

from pydantic import BaseModel, Field, validator
from typing import Optional


class LeadMagnetCreate(BaseModel):
    title: str
    lead_course_id: int
    upsell_course_id: int

    @validator("upsell_course_id")
    def ids_must_differ(cls, v, values):
        if "lead_course_id" in values and v == values["lead_course_id"]:
            raise ValueError("Курс-лид и курс-апселл не могут совпадать")
        return v


class LeadMagnetRead(BaseModel):
    id: int
    title: str
    lead_course_id: int
    upsell_course_id: int

    class Config:
        orm_mode = True
