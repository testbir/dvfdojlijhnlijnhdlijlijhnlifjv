# catalog_service/models/module.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.base import Base

class Module(Base):
    __tablename__ = "courses_module"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"))
    group_title = Column(String(255))
    title = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False)

    course = relationship("Course", back_populates="modules")

    content_blocks = relationship(
        "ContentBlock", back_populates="module", cascade="all, delete-orphan", passive_deletes=True
    )

    progresses = relationship(
        "UserModuleProgress", back_populates="module", cascade="all, delete-orphan", passive_deletes=True
    )
