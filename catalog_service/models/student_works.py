# catalog_service/models/student_works.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from core.base import Base

class StudentWorksSection(Base):
    __tablename__ = "student_works_sections"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)  # "Работы учеников нашего курса"
    description = Column(Text, nullable=False)  # Описание секции
    
    course = relationship("Course", back_populates="student_works_sections")
    works = relationship(
        "StudentWork",
        back_populates="section",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class StudentWork(Base):
    __tablename__ = "student_works"

    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("student_works_sections.id", ondelete="CASCADE"), nullable=False)
    image = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    bot_tag = Column(String(100), nullable=True)
    order = Column(Integer, default=0)

    section = relationship("StudentWorksSection", back_populates="works")