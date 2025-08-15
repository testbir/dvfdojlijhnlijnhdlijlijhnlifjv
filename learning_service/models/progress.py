# learning_service/models/progress.py


from sqlalchemy import Column, Integer, DateTime, UniqueConstraint, ForeignKey, func
from learning_service.core.base import Base

class UserModuleProgress(Base):
    __tablename__ = "learning_user_module_progress"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    module_id = Column(Integer, ForeignKey("learning_modules.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime, server_default=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "module_id", name="uq_user_module"),)
