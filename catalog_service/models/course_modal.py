# catalog_service/models/course_modal.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.base import Base

class CourseModal(Base):
    __tablename__ = "course_modals"
    __table_args__ = (UniqueConstraint("course_id", name="uq_course_modal_course"),)

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)

    course = relationship("Course", back_populates="modal")   # ← было backref="modals"

class CourseModalBlock(Base):
    __tablename__ = "course_modal_blocks"

    id = Column(Integer, primary_key=True)
    modal_id = Column(Integer, ForeignKey("course_modals.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, default=0)

    modal = relationship("CourseModal", back_populates="blocks")

# если блока blocks нет — добавь/оставь так:
CourseModal.blocks = relationship(
    "CourseModalBlock",
    back_populates="modal",
    cascade="all, delete-orphan",
    passive_deletes=True,
)
