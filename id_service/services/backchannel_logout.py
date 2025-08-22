# id_service/services/backchannel_logout.py

import asyncio
import logging
import secrets
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from jose import jwt
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.session import async_session_maker

from models import Client, RefreshToken, User
from core.config import settings
from services.jwk_service import jwk_service

logger = logging.getLogger(__name__)


class BackchannelLogoutService:
    """Service for handling back-channel logout notifications"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def initiate_backchannel_logout(
        self,
        session: Optional[AsyncSession],
        user: User,
        session_id: Optional[str] = None,
        reason: str = "user_logout",
        only_client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiate back-channel logout for all user's active sessions"""
        owns_session = False
        if session is None:
            owns_session = True
            session_ctx = async_session_maker()
            session = await session_ctx.__aenter__()
        try:
            active_clients = await self._get_user_active_clients(session, user.id, session_id, only_client_id)
            
            if not active_clients:
                logger.info(f"No active clients found for user {user.id}")
                return {"notified_clients": [], "failed_clients": []}
            
            # Create logout tasks for each client
            tasks = []
            for client in active_clients:
                if client.backchannel_logout_uri:
                    task = self._send_logout_notification(
                        client=client,
                        user=user,
                        session_id=session_id,
                        reason=reason
                    )
                    tasks.append((client.client_id, task))
            
            # Execute all logout notifications concurrently
            notified_clients = []
            failed_clients = []
            
            if tasks:
                results = await asyncio.gather(
                    *[task for _, task in tasks],
                    return_exceptions=True
                )
                
                for (client_id, _), result in zip(tasks, results):
                    if isinstance(result, Exception):
                        logger.error(f"Failed to notify client {client_id}: {result}")
                        failed_clients.append(client_id)
                    elif result:
                        notified_clients.append(client_id)
                    else:
                        failed_clients.append(client_id)
            
            logger.info(
                f"Back-channel logout completed for user {user.id}. "
                f"Notified: {len(notified_clients)}, Failed: {len(failed_clients)}"
            )
        
            return {
                "notified_clients": notified_clients,
                "failed_clients": failed_clients,
                "reason": reason
            }
        finally:
            if owns_session:
                await session_ctx.__aexit__(None, None, None)

    async def _get_user_active_clients(
        self,
        session: AsyncSession,
        user_id: str,
        session_id: Optional[str] = None,
        only_client_id: Optional[str] = None
    ) -> List[Client]:
        """Get all clients with active sessions or tokens for a user"""
        client_ids: set[str] = set()
        clients: list[Client] = []

        q = select(RefreshToken).where(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        )
        if only_client_id:
            q = q.where(RefreshToken.client_id == only_client_id)

        result = await session.execute(q)
        tokens = result.scalars().all()
        for token in tokens:
            if token.client_id not in client_ids:
                cres = await session.execute(select(Client).where(Client.client_id == token.client_id))
                client = cres.scalar_one_or_none()
                if client:
                    client_ids.add(client.client_id)
                    clients.append(client)

        return clients

    
    async def _send_logout_notification(
        self,
        client: Client,
        user: User,
        session_id: Optional[str] = None,
        reason: str = "user_logout"
    ) -> bool:
        """Send logout notification to a single client"""
        
        if not client.backchannel_logout_uri:
            logger.warning(f"Client {client.client_id} has no backchannel logout URI")
            return False
        
        try:
            # Create logout token
            logout_token = await self._create_logout_token(
                client=client,
                user=user,
                session_id=session_id
            )
            
            # Send POST request to client's backchannel logout URI
            response = await self.http_client.post(
                client.backchannel_logout_uri,
                data={"logout_token": logout_token},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                follow_redirects=False
            )
            
            # Check response
            if response.status_code == 200:
                logger.info(
                    f"Successfully notified client {client.client_id} "
                    f"for user {user.id} logout (reason: {reason})"
                )
                return True
            else:
                logger.warning(
                    f"Client {client.client_id} returned {response.status_code} "
                    f"for logout notification"
                )
                return False
                
        except httpx.TimeoutException:
            logger.error(f"Timeout notifying client {client.client_id}")
            return False
        except Exception as e:
            logger.error(f"Error notifying client {client.client_id}: {e}")
            return False
    
    async def _create_logout_token(
        self,
        client: Client,
        user: User,
        session_id: Optional[str] = None
    ) -> str:
        """Create a logout token according to OIDC Back-Channel Logout spec"""
        
        # Get active JWK key
        jwk_key = await jwk_service.get_active_key()
        if not jwk_key:
            raise RuntimeError("No active JWK key available")
        
        # Decrypt private key
        private_key_pem = jwk_service.decrypt_private_key(jwk_key.private_pem_encrypted)
        
        now = datetime.now(timezone.utc)
        
        # Create logout token claims
        claims = {
            "iss": settings.ISSUER,
            "aud": client.client_id,
            "iat": int(now.timestamp()),
            "jti": secrets.token_urlsafe(16),
            "events": {
                "http://schemas.openid.net/event/backchannel_logout": {}
            }
        }
        
        # Add either sub or sid (or both)
        if session_id:
            claims["sid"] = session_id
        
        claims["sub"] = str(user.id)
        
        # Sign the token
        logout_token = jwt.encode(
            claims,
            private_key_pem,
            algorithm="RS256",
            headers={"kid": jwk_key.kid}
        )
        
        return logout_token
    
    async def cleanup(self):
        """Cleanup HTTP client"""
        await self.http_client.aclose()


# Global instance
backchannel_logout_service = BackchannelLogoutService()