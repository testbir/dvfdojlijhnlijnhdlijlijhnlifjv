# catalog_service/models/lead_magnet.py

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from core.base import Base

class LeadMagnet(Base):
    __tablename__ = "marketing_lead_magnets"
    __table_args__ = (
        UniqueConstraint('lead_course_id', 'upsell_course_id', name='uq_lead_upsell_pair'),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    lead_course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)
    upsell_course_id = Column(Integer, ForeignKey("courses_course.id", ondelete="CASCADE"), nullable=False)

    lead_course = relationship("Course", foreign_keys=[lead_course_id])
    upsell_course = relationship("Course", foreign_keys=[upsell_course_id])
