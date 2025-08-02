# catalog_service/models/progress.py



from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from core.base import Base

class UserModuleProgress(Base):
    __tablename__ = "courses_usermoduleprogress"
    __table_args__ = (UniqueConstraint("user_id", "module_id", name="uix_user_module"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    module_id = Column(Integer, ForeignKey("courses_module.id", ondelete="CASCADE"))
    completed_at = Column(DateTime, default=datetime.utcnow)

    module = relationship("Module", back_populates="progresses")
