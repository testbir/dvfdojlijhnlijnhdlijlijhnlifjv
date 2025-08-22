# id_service/api/account/email_change.py

import logging
import asyncio
from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.account import (
    ChangeEmailRequest, ChangeEmailResponse,
    ConfirmEmailChangeRequest, ConfirmEmailChangeResponse
)
from api.account.profile import get_current_user
from services.email_service import email_service
from services.session_service import session_service
from services.backchannel_logout import backchannel_logout_service
from crud import user_crud
from utils.otp import otp_service
from utils.rate_limit import rate_limiter
from models import EmailCodePurpose
from core.security import security

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/change-email/request", response_model=ChangeEmailResponse)
async def request_email_change(
    request: Request,
    change_data: ChangeEmailRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    """Request email change - sends verification code to new email"""
    
    # Rate limit
    await rate_limiter.check_rate_limit(request, "email_change", max_requests=3)
    
    # Verify current password
    if not security.verify_password(change_data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Check if new email already exists
    if await user_crud.check_email_exists(
        session, 
        change_data.new_email,
        exclude_user_id=str(current_user.id)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use"
        )
    
    # Generate and send verification code to NEW email
    try:
        otp_code, email_code = await otp_service.create_otp(
            session=session,
            user=current_user,
            purpose=EmailCodePurpose.CHANGE_EMAIL,
            new_email=change_data.new_email,
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent")
        )
        
        # Send verification email to NEW address
        await email_service.send_verification_code(
            to_email=change_data.new_email,
            username=current_user.username,
            code=otp_code,
            purpose="change_email"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    
    logger.info(f"Email change requested for user {current_user.id}")
    
    return ChangeEmailResponse(
        message="Verification code sent to new email address"
    )


@router.post("/change-email/confirm", response_model=ConfirmEmailChangeResponse)
async def confirm_email_change(
    request: Request,
    confirm_data: ConfirmEmailChangeRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_user),
    response: Response = None,
):
    """Confirm email change with verification code"""
    
    # Rate limit
    await rate_limiter.check_rate_limit(request, "email_confirm", max_requests=10)
    
    # Verify OTP
    success, email_code, error = await otp_service.verify_otp(
        session=session,
        user_id=str(current_user.id),
        code=confirm_data.code,
        purpose=EmailCodePurpose.CHANGE_EMAIL
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Invalid verification code"
        )
    
    # Verify the new email matches
    if email_code.new_email != confirm_data.new_email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email mismatch"
        )
    
    # Update email
    from schemas.user import UserUpdate
    user_update = UserUpdate(
        email=confirm_data.new_email,
        email_verified=True
    )
    await user_crud.update(session, current_user, user_update)
    
    # Revoke SSO sessions
    _ = await session_service.revoke_all_user_sessions(session, str(current_user.id))

    # Очистить SSO cookie
    if response is not None:
        session_service.clear_session_cookie(response)

    # Revoke refresh tokens and notify clients
    from services.token_service import token_service
    affected = await token_service.revoke_all_refresh_tokens_for_user(
        session, str(current_user.id), reason="email_changed"
    )

    
    for cid in affected:
        asyncio.create_task(
            backchannel_logout_service.initiate_backchannel_logout(
                session=None,
                user=current_user,
                session_id=None,
                reason="email_changed",
                only_client_id=cid
            )
        )

    
    logger.info(f"Email changed for user {current_user.id}")
    
    return ConfirmEmailChangeResponse(
        message="Email address updated successfully"
    )