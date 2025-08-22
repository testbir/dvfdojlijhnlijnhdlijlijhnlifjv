# id_service/api/account/password_change.py


import logging
import asyncio
from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.account import ChangePasswordRequest, ChangePasswordResponse
from api.account.profile import get_current_user
from services.email_service import email_service
from services.session_service import session_service
from services.backchannel_logout import backchannel_logout_service
from crud import user_crud
from core.security import security

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: Request,
    change_data: ChangePasswordRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_user),
    response: Response = None
):
    """Change password for authenticated user"""
    
    # Verify old password
    if not security.verify_password(change_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Check new password is different
    if change_data.old_password == change_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    await user_crud.update_password(session, current_user, change_data.new_password)
    
    # Revoke all sessions
    _ = await session_service.revoke_all_user_sessions(session, str(current_user.id))

    # Очистить SSO cookie
    if response is not None:
        session_service.clear_session_cookie(response)

        
    
    # Revoke all refresh tokens and notify clients
    from services.token_service import token_service
    affected = await token_service.revoke_all_refresh_tokens_for_user(
        session, str(current_user.id), reason="password_changed"
    )
    for cid in affected:

        asyncio.create_task(
            backchannel_logout_service.initiate_backchannel_logout(
                session=None, user=current_user, session_id=None, reason="password_changed", only_client_id=cid
            )
        )
    

    
    logger.info(f"Password changed for user {current_user.id}")
    
    return ChangePasswordResponse(
        message="Password changed successfully"
    )