# id_service/utils/otp.py

from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import noload

from models import EmailCode, EmailCodePurpose, User
from core.config import settings
from core.security import security

import logging
logger = logging.getLogger(__name__)


class OTPService:
    """Service for managing OTP codes"""
    
    async def create_otp(
        self,
        session: AsyncSession,
        user: User,
        purpose: EmailCodePurpose,
        new_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, EmailCode]:
        """Create new OTP code"""
        
        # Check for existing active code
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(EmailCode).where(
                and_(
                    EmailCode.user_id == user.id,
                    EmailCode.purpose == purpose,
                    EmailCode.expires_at > now,
                    EmailCode.used_at.is_(None)
                )
            )
        )
        existing_code = result.scalar_one_or_none()
        
        if existing_code:
            # Check resend cooldown
            if existing_code.resend_after > now:
                seconds_left = int((existing_code.resend_after - now).total_seconds())
                raise ValueError(f"Please wait {seconds_left} seconds before requesting a new code")
            
            # Invalidate old code
            existing_code.used_at = now
        
        # Generate new OTP
        otp = security.generate_otp(4)
        otp_hash = security.hash_otp(otp)
        
        # Create email code record
        email_code = EmailCode(
            user_id=user.id,
            purpose=purpose,
            code_hash=otp_hash,
            new_email=new_email,
            expires_at=now + timedelta(seconds=settings.OTP_TTL),
            resend_after=now + timedelta(seconds=settings.OTP_RESEND_SECONDS),
            attempts=0,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        session.add(email_code)
        await session.flush()
        
        logger.info(f"Created OTP for user {user.id} with purpose {purpose}")
        return otp, email_code
    
    async def verify_otp(
        self,
        session: AsyncSession,
        user_id: str,
        code: str,
        purpose: EmailCodePurpose
    ) -> Tuple[bool, Optional[EmailCode], Optional[str]]:
        """
        Verify OTP code
        
        Returns:
            Tuple of (success, email_code if valid, error_message if invalid)
        """
        now = datetime.now(timezone.utc)
        
        # Find active code
        stmt = (
            select(EmailCode)
            .options(noload(EmailCode.user))  # опционально: уберёт LEFT OUTER JOIN
            .where(
                and_(
                    EmailCode.user_id == user_id,
                    EmailCode.purpose == purpose,
                    EmailCode.expires_at > now,
                    EmailCode.used_at.is_(None),
                )
            )
            .order_by(EmailCode.expires_at.desc())
            .with_for_update(of=[EmailCode])
        )
        result = await session.execute(stmt)
        email_code = result.scalar_one_or_none()
        
        if not email_code:
            return False, None, "No valid code found"
        
        # Check attempts
        email_code.attempts += 1
        
        if email_code.attempts > settings.OTP_MAX_ATTEMPTS:
            email_code.used_at = now  # Invalidate code
            await session.flush()
            return False, None, "Too many attempts. Please request a new code"
        
        # Verify code with constant time comparison
        code_hash = security.hash_otp(code)
        if not security.constant_time_compare(code_hash, email_code.code_hash):
            await session.flush()
            attempts_left = settings.OTP_MAX_ATTEMPTS - email_code.attempts
            return False, None, f"Invalid code. {attempts_left} attempts remaining"
        
        # Mark as used
        email_code.used_at = now
        await session.flush()
        
        logger.info(f"Successfully verified OTP for user {user_id} with purpose {purpose}")
        return True, email_code, None
    
    async def cleanup_expired_codes(
        self,
        session: AsyncSession
    ) -> int:
        """Clean up expired OTP codes (for maintenance)"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=1)
        
        result = await session.execute(
            select(EmailCode).where(
                EmailCode.expires_at < cutoff_date
            )
        )
        expired_codes = result.scalars().all()
        
        for code in expired_codes:
            session.delete(code)
        
        await session.flush()
        
        count = len(expired_codes)
        if count > 0:
            logger.info(f"Cleaned up {count} expired OTP codes")
        
        return count


otp_service = OTPService()