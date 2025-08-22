# id_service/api/auth/register.py

import logging
from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.auth import RegisterRequest, RegisterResponse
from schemas.user import UserCreate
from crud import user_crud
from services.email_service import email_service
from utils.otp import otp_service
from utils.rate_limit import rate_limiter
from models import EmailCodePurpose

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: Request,
    register_data: RegisterRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """Register new user"""
    
    # Rate limit
    await rate_limiter.check_rate_limit(request, "register", max_requests=5)
    
    # Check if email already exists
    if await user_crud.check_email_exists(session, register_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if await user_crud.check_username_exists(session, register_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user_create = UserCreate(
        email=register_data.email,
        username=register_data.username,
        password=register_data.password,
        email_verified=False
    )
    
    user = await user_crud.create(session, user_create)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Generate and send verification code
    try:
        otp_code, email_code = await otp_service.create_otp(
            session=session,
            user=user,
            purpose=EmailCodePurpose.REGISTER,
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent")
        )
        
        # Send verification email
        await email_service.send_verification_code(
            to_email=user.email,
            username=user.username,
            code=otp_code,
            purpose="registration"
        )
        
    except ValueError as e:
        # OTP creation failed (cooldown)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        # Don't reveal email sending issues
    
    return RegisterResponse(
        user_id=str(user.id),
        message="Registration successful. Please check your email for verification code."
    )