# id_service/api/oidc/userinfo.py

import logging
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.oidc import UserInfoResponse
from services.token_service import token_service
from crud import user_crud

logger = logging.getLogger(__name__)
router = APIRouter()

security = HTTPBearer()


@router.get("/userinfo", response_model=UserInfoResponse)
@router.post("/userinfo", response_model=UserInfoResponse)
async def userinfo(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """OpenID Connect UserInfo endpoint"""
    
    # Verify access token
    token_claims = await token_service.verify_access_token(credentials.credentials)
    
    if not token_claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check scope
    scopes = token_claims.get("scope", "").split()
    
    # Get user
    user = await user_crud.get_by_id(session, token_claims["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Build response based on scopes
    response_data = {
        "sub": str(user.id)
    }
    
    if "email" in scopes:
        response_data["email"] = user.email
        response_data["email_verified"] = user.email_verified
    
    if "profile" in scopes:
        response_data["preferred_username"] = user.username
        if user.updated_at:
            response_data["updated_at"] = int(user.updated_at.timestamp())
    
    return UserInfoResponse(**response_data)