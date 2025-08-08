

# catalog_service/models/content.py

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.base import Base

class ContentBlock(Base):
    __tablename__ = "courses_contentblock"

    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("courses_module.id", ondelete="CASCADE"))
    title = Column(String(255))
    type = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    video_preview = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)  # Новое поле для языка программирования

    module = relationship("Module", back_populates="content_blocks")




