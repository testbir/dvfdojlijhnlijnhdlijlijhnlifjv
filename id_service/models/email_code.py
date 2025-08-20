# id_service/models/email_code.py

from datetime import datetime
from sqlalchemy import Column, Text, Index, String, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from db.base import Base


class EmailCodePurpose(str, enum.Enum):
    REGISTER = "register"
    RESET_PASSWORD = "reset"
    CHANGE_EMAIL = "change_email"


class EmailCode(Base):
    __tablename__ = "email_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Code details
    purpose = Column(Enum(EmailCodePurpose), nullable=False)
    code_hash = Column(String(255), nullable=False)
    new_email = Column(String(255), nullable=True)  # For email change
    
    # Security
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    attempts = Column(Integer, default=0, nullable=False)
    resend_after = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relations
    user = relationship("User", backref="email_codes", lazy="joined")
    
    __table_args__ = (
        Index('ix_email_codes_user_purpose', 'user_id', 'purpose', 'expires_at'),
    )