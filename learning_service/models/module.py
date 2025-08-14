# learning_service/models/module.py

from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from learning_service.core.base import Base

class Module(Base):
    __tablename__ = "learning_modules"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, nullable=False)  # внешний курс из catalog_service
    title = Column(String(255), nullable=False)
    group_title = Column(String(255), nullable=True)
    order = Column(Integer, default=1, nullable=False)

    # Skill Points за прохождение модуля (большие значения)
    sp_award = Column(BigInteger, default=0, nullable=False)

    # Одноразовый комментарий при первом завершении модуля
    completion_message = Column(Text, nullable=True)

    blocks = relationship("Block", back_populates="module", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("course_id", "title", name="uq_course_module_title"),
    )
