# id_service/crud/client.py

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models import Client, ClientType, TokenAuthMethod
from core.security import security

import logging
logger = logging.getLogger(__name__)


class ClientCRUD:
    """CRUD operations for Client model"""
    
    async def get_by_client_id(
        self,
        session: AsyncSession,
        client_id: str
    ) -> Optional[Client]:
        """Get client by client_id"""
        result = await session.execute(
            select(Client).where(Client.client_id == client_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        session: AsyncSession,
        client_id: str,
        name: str,
        client_type: ClientType = ClientType.PUBLIC,
        redirect_uris: List[str] = None,
        post_logout_redirect_uris: List[str] = None,
        backchannel_logout_uri: Optional[str] = None,
        frontchannel_logout_uri: Optional[str] = None,
        scopes: List[str] = None,
        client_secret: Optional[str] = None,
        pkce_required: bool = True
    ) -> Client:
        """Create new client"""
        
        # Hash client secret if provided
        client_secret_hash = None
        if client_secret:
            client_secret_hash = security.hash_password(client_secret)
        
        client = Client(
            client_id=client_id,
            name=name,
            type=client_type,
            token_endpoint_auth_method=(
                TokenAuthMethod.CLIENT_SECRET_POST 
                if client_type == ClientType.CONFIDENTIAL 
                else TokenAuthMethod.NONE
            ),
            pkce_required=pkce_required,
            redirect_uris=redirect_uris or [],
            post_logout_redirect_uris=post_logout_redirect_uris or [],
            backchannel_logout_uri=backchannel_logout_uri,
            frontchannel_logout_uri=frontchannel_logout_uri,
            scopes=scopes or ["openid", "email", "profile"],
            client_secret_hash=client_secret_hash,
            created_at=datetime.now(timezone.utc)
        )
        
        session.add(client)
        await session.flush()
        
        logger.info(f"Created client {client_id}")
        return client
    
    async def update(
        self,
        session: AsyncSession,
        client: Client,
        **kwargs
    ) -> Client:
        """Update client"""
        for key, value in kwargs.items():
            if hasattr(client, key):
                setattr(client, key, value)
        
        client.updated_at = datetime.now(timezone.utc)
        await session.flush()
        
        logger.info(f"Updated client {client.client_id}")
        return client
    
    async def rotate_secret(
        self,
        session: AsyncSession,
        client: Client,
        new_secret: str
    ) -> Client:
        """Rotate client secret"""
        client.client_secret_hash = security.hash_password(new_secret)
        client.secret_rotated_at = datetime.now(timezone.utc)
        client.updated_at = datetime.now(timezone.utc)
        
        await session.flush()
        
        logger.info(f"Rotated secret for client {client.client_id}")
        return client
    
    async def verify_secret(
        self,
        client: Client,
        secret: str
    ) -> bool:
        """Verify client secret"""
        if not client.client_secret_hash:
            return False
        
        return security.verify_password(secret, client.client_secret_hash)
    
    async def list_all(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[Client]:
        """List all clients"""
        result = await session.execute(
            select(Client)
            .order_by(Client.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()


client_crud = ClientCRUD()