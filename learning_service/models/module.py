# learning_service/models/module.py

from sqlalchemy import Column, Integer, String, Text, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from learning_service.core.base import Base

class Module(Base):
    __tablename__ = "learning_modules"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    group_title = Column(String(255), nullable=True)
    order = Column(Integer, default=1, nullable=False)

    sp_award = Column(BigInteger, default=0, nullable=False)
    completion_message = Column(Text, nullable=True)

    blocks = relationship("Block", back_populates="module", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("course_id", "title", name="uq_course_module_title"),
        UniqueConstraint("course_id", "order", name="uq_course_module_order"),
    )
