# catalog_service/models/access.py

from sqlalchemy import UniqueConstraint, Column, Integer, ForeignKey, DateTime
from datetime import datetime

from core.base import Base

class CourseAccess(Base):
    __tablename__ = "courses_courseaccess"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)
    purchased_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course"),)
