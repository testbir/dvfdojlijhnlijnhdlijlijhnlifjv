# id_service/models/jwk_key.py

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from db.base import Base


class JWKKey(Base):
    __tablename__ = "jwk_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kid = Column(String(255), unique=True, nullable=False, index=True)  # Key ID
    alg = Column(String(10), nullable=False, default="RS256")
    
    # Key material
    public_pem = Column(Text, nullable=False)
    private_pem_encrypted = Column(Text, nullable=False)  # Encrypted with app secret
    
    # Status
    active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    rotated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('ix_jwk_keys_active_kid', 'active', 'kid'),
    )