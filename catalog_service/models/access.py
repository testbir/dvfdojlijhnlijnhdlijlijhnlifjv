# catalog_service/models/acces.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from core.base import Base

class CourseAccess(Base):
    __tablename__ = "courses_courseaccess"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"))
    purchased_at = Column(DateTime, default=datetime.utcnow)
