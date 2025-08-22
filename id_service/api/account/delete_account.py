# id_service/api/account/delete_account.py


import logging
import asyncio
from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.account import DeleteAccountRequest, DeleteAccountResponse
from api.account.profile import get_current_user
from services.session_service import session_service
from services.backchannel_logout import backchannel_logout_service
from crud import user_crud
from core.security import security

logger = logging.getLogger(__name__)
router = APIRouter()


@router.delete("/delete", response_model=DeleteAccountResponse)
async def delete_account(
    request: Request,
    delete_data: DeleteAccountRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_user),
    response: Response = None,
):
    """Delete user account (soft delete)"""
    
    # Verify password
    if not security.verify_password(delete_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Verify confirmation
    if delete_data.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please type DELETE to confirm"
        )
    
    # Revoke all sessions
    _ = await session_service.revoke_all_user_sessions(session, str(current_user.id))

    # Очистить SSO cookie
    if response is not None:
        session_service.clear_session_cookie(response)

    # Revoke all refresh tokens and notify clients
    from services.token_service import token_service
    affected = await token_service.revoke_all_refresh_tokens_for_user(
        session, str(current_user.id), reason="account_deleted"
    )

    for cid in affected:
        asyncio.create_task(
            backchannel_logout_service.initiate_backchannel_logout(
                session=None,
                user=current_user,
                session_id=None,
                reason="account_deleted",
                only_client_id=cid
            )
        )

    
    # Soft delete user
    await user_crud.soft_delete(session, current_user)
    
    logger.info(f"Account deleted for user {current_user.id}")
    
    return DeleteAccountResponse(
        message="Account has been deleted"
    )