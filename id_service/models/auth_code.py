# id_service/models/auth_code.py

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from db.base import Base


class AuthCode(Base):
    __tablename__ = "auth_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Relations
    client_id = Column(String(255), ForeignKey("clients.client_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # OIDC parameters
    redirect_uri = Column(Text, nullable=False)
    scope = Column(String(500), nullable=False)
    code_challenge_hash = Column(String(255), nullable=True)  # For PKCE
    nonce = Column(String(255), nullable=True)
    state = Column(String(500), nullable=True)
    
    # Security
    auth_time = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relations
    client = relationship("Client", backref="auth_codes", lazy="joined")
    user = relationship("User", backref="auth_codes", lazy="joined")