# catalog_service/models/promocode.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from datetime import datetime

from catalog_service.core.base import Base

class PromoCode(Base):
    __tablename__ = "promocodes"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_percent = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    uses_left = Column(Integer, default=0)
    max_uses = Column(Integer, default=0)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    applicable_courses = Column(JSON, default=list)