# id_service/models/idp_session.py

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from db.base import Base


class IDPSession(Base):
    __tablename__ = "idp_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)  # sid for OIDC
    
    # Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Session tracking
    last_seen_at = Column(DateTime(timezone=True), nullable=False)
    idle_expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    max_expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Status
    created_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    user = relationship("User", backref="idp_sessions", lazy="joined")
    
    __table_args__ = (
        Index('ix_idp_sessions_user_revoked', 'user_id', 'revoked_at'),
    )