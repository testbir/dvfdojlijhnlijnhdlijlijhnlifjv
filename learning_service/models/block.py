# learning_service/models/block.py

from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from learning_service.core.base import Base

class Block(Base):
    __tablename__ = "learning_blocks"

    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)   # text | image | video | code
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    order = Column(Integer, default=1, nullable=False)

    language = Column(String(50), nullable=True)
    video_preview = Column(Text, nullable=True)

    module = relationship("Module", back_populates="blocks")

    __table_args__ = (
        UniqueConstraint("module_id", "order", name="uq_block_order_in_module"),
    )
