# id_service/services/session_service.py


import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import Request, Response, Cookie

from models import IDPSession, User
from core.config import settings
from core.security import security

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing SSO sessions"""
    
    def __init__(self):
        self.cookie_name = "id_session"
        self.cookie_domain = "id.asynq.ru" if settings.APP_ENV == "production" else None
    
    async def create_session(
        self,
        session: AsyncSession,
        user: User,
        request: Request,
        remember_me: bool = False,   # <— добавили
    ) -> IDPSession:
        session_id = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)

        max_ttl = settings.SSO_MAX_TTL if not remember_me else 30*24*3600

        idp_session = IDPSession(
            session_id=session_id,
            user_id=user.id,
            last_seen_at=now,
            idle_expires_at=now + timedelta(seconds=settings.SSO_IDLE_TTL),
            max_expires_at=now + timedelta(seconds=max_ttl),  # <— было SSO_MAX_TTL
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            created_at=now
        )
        session.add(idp_session)
        await session.flush()
        return idp_session

    
    async def get_session(
        self,
        session: AsyncSession,
        session_id: str
    ) -> Optional[IDPSession]:
        """Get valid session by ID"""
        now = datetime.now(timezone.utc)
        
        result = await session.execute(
            select(IDPSession).where(
                and_(
                    IDPSession.session_id == session_id,
                    IDPSession.revoked_at.is_(None),
                    IDPSession.idle_expires_at > now,
                    IDPSession.max_expires_at > now
                )
            )
        )
        
        idp_session = result.scalar_one_or_none()
        
        if idp_session:
            # Update last seen and idle timeout
            idp_session.last_seen_at = now
            idp_session.idle_expires_at = now + timedelta(seconds=settings.SSO_IDLE_TTL)
            await session.flush()
        
        return idp_session
    
    async def get_session_from_cookie(
        self,
        session: AsyncSession,
        request: Request
    ) -> Optional[IDPSession]:
        """Get session from request cookie"""
        session_cookie = request.cookies.get(self.cookie_name)
        if not session_cookie:
            return None
        
        return await self.get_session(session, session_cookie)
    
    def set_session_cookie(
        self,
        response: Response,
        session_id: str,
        max_age: int | None = None,
    ) -> None:
        response.set_cookie(
            key=self.cookie_name,
            value=session_id,
            domain=self.cookie_domain,
            path="/",
            secure=settings.APP_ENV == "production",
            httponly=True,
            samesite="lax",
            max_age=max_age or settings.SSO_MAX_TTL,
        )
    
    def clear_session_cookie(self, response: Response) -> None:
        """Clear SSO session cookie"""
        response.delete_cookie(
            key=self.cookie_name,
            domain=self.cookie_domain,
            path="/"
        )
    
    async def revoke_session(
        self,
        session: AsyncSession,
        idp_session: IDPSession
    ) -> None:
        """Revoke SSO session"""
        idp_session.revoked_at = datetime.now(timezone.utc)
        await session.flush()
    
    async def revoke_all_user_sessions(
        self,
        session: AsyncSession,
        user_id: str
    ) -> List[IDPSession]:
        """Revoke all sessions for a user"""
        result = await session.execute(
            select(IDPSession).where(
                and_(
                    IDPSession.user_id == user_id,
                    IDPSession.revoked_at.is_(None)
                )
            )
        )
        
        sessions = result.scalars().all()
        now = datetime.now(timezone.utc)
        
        for idp_session in sessions:
            idp_session.revoked_at = now
        
        await session.flush()
        return sessions
    
    async def get_active_user_sessions(
        self,
        session: AsyncSession,
        user_id: str
    ) -> List[IDPSession]:
        """Get all active sessions for a user"""
        now = datetime.now(timezone.utc)
        
        result = await session.execute(
            select(IDPSession).where(
                and_(
                    IDPSession.user_id == user_id,
                    IDPSession.revoked_at.is_(None),
                    IDPSession.max_expires_at > now
                )
            )
        )
        
        return result.scalars().all()


session_service = SessionService()