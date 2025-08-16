# catalog_service/models/course_modal.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from core.base import Base

class CourseModal(Base):
    __tablename__ = "course_modals"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)  # Заголовок модального окна
    
    course = relationship("Course", backref="modals")
    blocks = relationship(
        "CourseModalBlock",
        back_populates="modal",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class CourseModalBlock(Base):
    __tablename__ = "course_modal_blocks"

    id = Column(Integer, primary_key=True)
    modal_id = Column(Integer, ForeignKey("course_modals.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, default=0)

    modal = relationship("CourseModal", back_populates="blocks")