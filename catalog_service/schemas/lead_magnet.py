# catalog_service/schemas/lead_magnet.py

from pydantic import BaseModel, ConfigDict, model_validator

class LeadMagnetCreate(BaseModel):
    title: str
    lead_course_id: int
    upsell_course_id: int

    @model_validator(mode="after")
    def check_ids(self):
        if self.lead_course_id == self.upsell_course_id:
            raise ValueError("Курс-лид и курс-апселл не могут совпадать")
        return self



class LeadMagnetRead(BaseModel):
    id: int
    title: str
    lead_course_id: int
    upsell_course_id: int

    model_config = ConfigDict(from_attributes=True)
