# catalog_service/models/user_position.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from core.base import Base

class UserCoursePosition(Base):
    """
    Сохраняет текущую позицию пользователя в курсе
    Для быстрого возврата к последнему месту обучения
    """
    __tablename__ = "user_course_positions"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uix_user_course_position"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)
    current_module_id = Column(Integer, ForeignKey("courses_module.id", ondelete="CASCADE"), nullable=True)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Дополнительная информация для аналитики
    total_time_spent = Column(Integer, default=0)  # в секундах
    
    # Связи
    course = relationship("Course")
    current_module = relationship("Module")

class UserLearningSession(Base):
    """
    Отслеживает сессии обучения для аналитики
    """
    __tablename__ = "user_learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("courses_module.id", ondelete="CASCADE"), nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    time_spent = Column(Integer, default=0)  # в секундах
    
    # Связи
    course = relationship("Course")
    module = relationship("Module")