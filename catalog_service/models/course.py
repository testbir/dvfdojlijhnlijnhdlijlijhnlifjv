# catalog_service/models/course.py

from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship

from core.base import Base

class Course(Base):
    __tablename__ = "courses_course"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    short_description = Column(Text, nullable=False)
    full_description = Column(Text, nullable=True)
    image = Column(Text, nullable=True)
    is_free = Column(Boolean, default=False)
    price = Column(DECIMAL(10, 2), nullable=True)
    discount = Column(DECIMAL(5, 2), default=0.0)

    # 🎬 Новые поля
    video = Column(Text, nullable=True)
    video_preview = Column(Text, nullable=True)
    
    banner_text = Column(Text, nullable=True)
    banner_color_left = Column(String(20), nullable=True)
    banner_color_right = Column(String(20), nullable=True)
    order = Column(Integer, default=0)
        
    discount_start = Column(DateTime(timezone=True), nullable=True)
    discount_until = Column(DateTime(timezone=True), nullable=True)
    
    
    group_title = Column(String(100), nullable=True)
    
    modal = relationship(
        "CourseModal",
        back_populates="course",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    student_works_sections = relationship(
        "StudentWorksSection",
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )