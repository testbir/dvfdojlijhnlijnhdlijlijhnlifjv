# id_service/api/auth/email_verification.py
"""
Подтверждение e-mail — JSON-only.

Изменения:
- Убраны любые RedirectResponse.
- При наличии валидного pending state в Redis формируем redirect_to строкой без 302.
- Всегда ставим SSO-cookie на JSON-ответ.
"""

import logging
import json
from urllib.parse import urlencode

from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.auth import VerifyEmailRequest, VerifyEmailResponse
from crud import user_crud, client_crud
from services.session_service import session_service
from services.token_service import token_service
from utils.otp import otp_service
from utils.rate_limit import rate_limiter
from utils.validators import validators
from models import EmailCodePurpose
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: Request,
    response: Response,
    verify_data: VerifyEmailRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Подтверждение e-mail по OTP коду.
    Поведение:
      - Если есть pending /authorize по state и redirect валиден — выпускаем code,
        привязываем sid, удаляем pending, возвращаем JSON с redirect_to.
      - Иначе обычный JSON без redirect_to.
      - ВО ВСЕХ случаях ставим SSO-cookie на этот JSON-ответ.
    """
    # 1) Rate limit
    await rate_limiter.check_rate_limit(request, "verify_email", max_requests=10)

    # 2) Пользователь
    user = await user_crud.get_by_id(session, verify_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 3) Проверка OTP
    success, email_code, error = await otp_service.verify_otp(
        session=session,
        user_id=verify_data.user_id,
        code=verify_data.code,
        purpose=EmailCodePurpose.REGISTER,
    )
    if not success:
        await rate_limiter.add_failed_attempt(verify_data.user_id, "otp_verify", max_attempts=5)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error or "Invalid verification code")

    # 4) Отметить e-mail как верифицированный и очистить счётчик
    await user_crud.verify_email(session, user)
    await rate_limiter.clear_failed_attempts(verify_data.user_id, "otp_verify")

    # 5) Создать IdP-сессию
    idp_session = await session_service.create_session(session=session, user=user, request=request)

    # 6) OIDC-продолжение: собрать redirect_to, если есть валидный pending по state
    redirect_to: str | None = None
    if verify_data.state and rate_limiter.redis_client:
        raw = await rate_limiter.redis_client.get(f"authreq:{verify_data.state}")
        if raw:
            data = json.loads(raw)
            client = await client_crud.get_by_client_id(session, data.get("client_id"))
            redirect_uri = data.get("redirect_uri")
            if client and validators.validate_redirect_uri(redirect_uri, client.redirect_uris or []):
                # Выпустить authorization code
                code = await token_service.create_auth_code(
                    session=session,
                    user=user,
                    client=client,
                    redirect_uri=redirect_uri,
                    scope=data.get("scope", ""),
                    state=verify_data.state,
                    nonce=data.get("nonce"),
                    code_challenge=data.get("code_challenge"),
                    ip_address=request.client.host,
                    user_agent=request.headers.get("User-Agent"),
                )
                # Привязать sid к коду и удалить pending
                await rate_limiter.redis_client.setex(
                    f"authcode_sid:{code}", settings.AUTH_CODE_TTL, idp_session.session_id
                )
                await rate_limiter.redis_client.delete(f"authreq:{verify_data.state}")

                params = {"code": code, "state": verify_data.state}
                redirect_to = f"{redirect_uri}?{urlencode(params)}"

    # 7) Кука SSO — на текущий JSON-ответ
    session_service.set_session_cookie(response, idp_session.session_id)

    logger.info(f"Email verified for user {user.id}")
    return VerifyEmailResponse(ok=True, message="Email verified successfully", redirect_to=redirect_to)
