# id_service/models/refresh_token.py

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jti = Column(String(255), unique=True, nullable=False, index=True)  # JWT ID
    
    # Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    client_id = Column(String(255), ForeignKey("clients.client_id"), nullable=False)
    
    # Token chain (for rotation)
    parent_jti = Column(String(255), nullable=True, index=True)  # Parent token that created this
    prev_jti = Column(String(255), nullable=True)  # Previous token in rotation chain
    
    # Scope
    scope = Column(String(500), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    rotated_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(String(255), nullable=True)
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relations
    user = relationship("User", backref="refresh_tokens", lazy="joined")
    client = relationship("Client", backref="refresh_tokens", lazy="joined")
    
    __table_args__ = (
        Index('ix_refresh_tokens_user_client', 'user_id', 'client_id', 'revoked_at', 'expires_at'),
    )