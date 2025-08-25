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
async def register(request: Request, register_data: RegisterRequest, session: AsyncSession = Depends(get_async_session)):
    await rate_limiter.check_rate_limit(request, "register", max_requests=5)

    # смотрим существующий email
    existing = await user_crud.get_by_email(session, register_data.email)
    if existing:
        if existing.email_verified:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        # email есть, но не подтверждён — возвращаем user_id и (по возможности) переотправляем код
        try:
            otp_code, _ = await otp_service.create_otp(
                session=session,
                user=existing,
                purpose=EmailCodePurpose.REGISTER,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent"),
            )
            await email_service.send_verification_code(
                to_email=existing.email,
                username=existing.username,
                code=otp_code,
                purpose="registration",
            )
            msg = "Verification code sent"
        except ValueError:
            # кулдаун — всё равно возвращаем успешный ответ, чтобы фронт ушёл на страницу кода
            msg = "Verification code was sent recently. Please check your email."
        return RegisterResponse(
            user_id=str(existing.id),
            email=existing.email,
            requires_verification=True,
            message=msg,
        )

    # проверка уникальности username только для новых
    if await user_crud.check_username_exists(session, register_data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # создаём пользователя
    user = await user_crud.create(session, UserCreate(
        email=register_data.email,
        username=register_data.username,
        password=register_data.password,
        email_verified=False,
    ))

    # шлём код (ошибки отправки не валят регистрацию)
    msg = "Registration successful. Please check your email for verification code."
    try:
        otp_code, _ = await otp_service.create_otp(
            session=session,
            user=user,
            purpose=EmailCodePurpose.REGISTER,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
        )
        await email_service.send_verification_code(
            to_email=user.email,
            username=user.username,
            code=otp_code,
            purpose="registration",
        )
    except Exception:
        pass

    return RegisterResponse(
        user_id=str(user.id),
        email=user.email,
        requires_verification=True,
        message=msg,
    )