# id_service/crud/idp_session.py

from typing import Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from models import IDPSession

import logging
logger = logging.getLogger(__name__)


class IDPSessionCRUD:
    """CRUD operations for IDP Session model"""
    
    async def get_active_session(
        self,
        session: AsyncSession,
        session_id: str
    ) -> Optional[IDPSession]:
        """Get active session by ID"""
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
        return result.scalar_one_or_none()
    
    async def get_user_sessions(
        self,
        session: AsyncSession,
        user_id: str,
        only_active: bool = True
    ) -> List[IDPSession]:
        """Get all sessions for a user"""
        query = select(IDPSession).where(IDPSession.user_id == user_id)
        
        if only_active:
            now = datetime.now(timezone.utc)
            query = query.where(
                and_(
                    IDPSession.revoked_at.is_(None),
                    IDPSession.max_expires_at > now
                )
            )
        
        query = query.order_by(IDPSession.created_at.desc())
        
        result = await session.execute(query)
        return result.scalars().all()
    
    async def cleanup_expired(
        self,
        session: AsyncSession
    ) -> int:
        """Clean up expired sessions"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=7)  # Keep for 7 days after expiry
        
        result = await session.execute(
            select(IDPSession).where(
                or_(
                    IDPSession.max_expires_at < cutoff,
                    and_(
                        IDPSession.revoked_at.is_not(None),
                        IDPSession.revoked_at < cutoff
                    )
                )
            )
        )
        
        expired_sessions = result.scalars().all()
        
        for idp_session in expired_sessions:
            session.delete(idp_session)
        
        await session.flush()
        
        count = len(expired_sessions)
        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions")
        
        return count


idp_session_crud = IDPSessionCRUD()