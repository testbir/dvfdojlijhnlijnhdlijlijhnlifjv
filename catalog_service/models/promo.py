# catalog_service/models/promo.py

from sqlalchemy import Column, Integer, String, ForeignKey

from core.base import Base

class PromoImage(Base):
    __tablename__ = "homepage_promo_images"

    id = Column(Integer, primary_key=True)
    image = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses_course.id"), nullable=False)
    order = Column(Integer, default=0)
