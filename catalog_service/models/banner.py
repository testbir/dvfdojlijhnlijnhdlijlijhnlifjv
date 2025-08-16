# catalog_service/models/banner.py

from sqlalchemy import Column, Integer, String

from core.base import Base

class Banner(Base):
    __tablename__ = "homepage_banners"

    id = Column(Integer, primary_key=True)
    image = Column(String, nullable=False)
    order = Column(Integer, default=0)
    link = Column(String, nullable=True)
