# id_service/api/auth/password_reset.py


import logging
import asyncio
import secrets
from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.auth import (
    ForgotPasswordRequest, ForgotPasswordResponse,
    VerifyResetRequest, VerifyResetResponse,
    SetNewPasswordRequest, SetNewPasswordResponse
)
from utils.rate_limit import rate_limiter
from crud import user_crud
from services.email_service import email_service
from services.session_service import session_service
from services.backchannel_logout import backchannel_logout_service
from services.token_service import token_service
from utils.otp import otp_service
from models import EmailCodePurpose

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: Request,
    forgot_data: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """Request password reset"""
    
    # Rate limit
    await rate_limiter.check_rate_limit(request, "forgot_password", max_requests=3)
    
    # Always return same response for security
    response_message = "If an account exists with this email, a reset code has been sent"
    
    # Find user
    user = await user_crud.get_by_email(session, forgot_data.email)
    if user:
        try:
            # Generate and send reset code
            otp_code, email_code = await otp_service.create_otp(
                session=session,
                user=user,
                purpose=EmailCodePurpose.RESET_PASSWORD,
                ip_address=request.client.host,
                user_agent=request.headers.get("User-Agent")
            )
            
            # Send reset email
            await email_service.send_verification_code(
                to_email=user.email,
                username=user.username,
                code=otp_code,
                purpose="reset"
            )
            
            logger.info(f"Password reset requested for user {user.id}")
            
        except Exception as e:
            logger.error(f"Failed to process password reset: {e}")
    
    return ForgotPasswordResponse(message=response_message)


@router.post("/verify-reset", response_model=VerifyResetResponse)
async def verify_reset(
    request: Request,
    verify_data: VerifyResetRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """Verify password reset code"""
    
    # Rate limit
    await rate_limiter.check_rate_limit(request, "verify_reset", max_requests=10)
    
    # Find user
    user = await user_crud.get_by_email(session, verify_data.email)
    if not user:
        # одинаковый ответ, без утечки наличия e-mail
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or code"
        )

    
    # Verify OTP
    success, email_code, error = await otp_service.verify_otp(
        session=session,
        user_id=str(user.id),
        code=verify_data.code,
        purpose=EmailCodePurpose.RESET_PASSWORD
    )
    
    if not success:
        await rate_limiter.add_failed_attempt(
            verify_data.email,
            "reset_verify",
            max_attempts=5
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Invalid reset code"
        )
    
    # Generate temporary reset token
    reset_token = secrets.token_urlsafe(32)
    # Store reset token in Redis (15 минут)
    if rate_limiter.redis_client:
        await rate_limiter.redis_client.setex(
            f"pwdreset:{user.id}", 900, reset_token
        )  
    
    return VerifyResetResponse(
        user_id=str(user.id),
        reset_token=reset_token
    )


@router.post("/set-new-password", response_model=SetNewPasswordResponse)
async def set_new_password(
    request: Request,
    reset_data: SetNewPasswordRequest,
    session: AsyncSession = Depends(get_async_session),
    response: Response = None,
):
    """Set new password after reset"""
    
    # Rate limit
    await rate_limiter.check_rate_limit(request, "set_password", max_requests=5)
    
    # Verify reset token (one-time)
    if not rate_limiter.redis_client:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Reset not available")
    stored = await rate_limiter.redis_client.get(f"pwdreset:{reset_data.user_id}")
    if not stored or stored != reset_data.reset_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
    await rate_limiter.redis_client.delete(f"pwdreset:{reset_data.user_id}")

    
    # Get user
    user = await user_crud.get_by_id(session, reset_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid reset token"
        )
    
    # Update password
    await user_crud.update_password(session, user, reset_data.new_password)

    # Revoke all sessions
    _ = await session_service.revoke_all_user_sessions(session, str(user.id))

    # Очистить SSO cookie
    if response is not None:
        session_service.clear_session_cookie(response)

    # Revoke all refresh tokens and notify clients
    
    affected = await token_service.revoke_all_refresh_tokens_for_user(
        session, str(user.id), reason="password_reset"
    )
    
    for cid in affected:
        asyncio.create_task(
            backchannel_logout_service.initiate_backchannel_logout(
                session=None, user=user, session_id=None, reason="password_reset", only_client_id=cid
            )
        )


    
    logger.info(f"Password reset completed for user {user.id}")
    
    return SetNewPasswordResponse(
        message="Password has been reset successfully"
    )