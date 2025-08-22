# id_service/api/account/profile.py

import logging
from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.account import ProfileResponse
from services.session_service import session_service
from crud import user_crud

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    """Dependency to get current authenticated user"""
    
    # Get session from cookie
    idp_session = await session_service.get_session_from_cookie(session, request)
    if not idp_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Get user
    user = await user_crud.get_by_id(session, idp_session.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    """Get current user profile"""
    
    return ProfileResponse(
        email=current_user.email,
        username=current_user.username,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )