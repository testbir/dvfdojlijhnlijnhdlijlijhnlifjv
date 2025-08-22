# id_service/models/client.py

from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import Column, String, Text, Boolean, DateTime, Enum, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from db.base import Base


class ClientType(str, enum.Enum):
    PUBLIC = "public"
    CONFIDENTIAL = "confidential"


class TokenAuthMethod(str, enum.Enum):
    NONE = "none"
    CLIENT_SECRET_POST = "client_secret_post"
    CLIENT_SECRET_BASIC = "client_secret_basic"


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)

    type = Column(Enum(ClientType), nullable=False, default=ClientType.PUBLIC)
    token_endpoint_auth_method = Column(
        Enum(TokenAuthMethod), nullable=False, default=TokenAuthMethod.NONE
    )
    pkce_required = Column(Boolean, nullable=False, default=True)

    redirect_uris = Column(JSONB, nullable=False, default=list)
    post_logout_redirect_uris = Column(JSONB, nullable=False, default=list)
    backchannel_logout_uri = Column(Text, nullable=True)
    frontchannel_logout_uri = Column(Text, nullable=True)

    scopes = Column(JSONB, nullable=False, default=lambda: ["openid", "email", "profile"])

    client_secret_hash = Column(Text, nullable=True)
    secret_rotated_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ux_clients_client_id", "client_id", unique=True),
    )
