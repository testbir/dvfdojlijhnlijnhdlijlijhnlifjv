# id_service/api/auth/login.py
"""
Логин по паролю — JSON-only.
Цели:
- Принимаем JSON (никаких Form(...)).
- Проверка CSRF уже в CSRFMiddleware по заголовку X-CSRF-Token.
- На успехе всегда ставим SSO-cookie на JSON-ответ.
- Если есть валидные state+client_id в Redis (pending /authorize) — создаём code и
  возвращаем redirect_to строкой без 302. Иначе redirect_to = null.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas.auth import LoginPasswordRequest, LoginPasswordResponse
from crud import user_crud, client_crud
from services.session_service import session_service
from services.token_service import token_service
from utils.rate_limit import rate_limiter
from utils.validators import validators
from core.security import security
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login-password", response_model=LoginPasswordResponse)
async def login_password(
    request: Request,
    response: Response,
    login_data: LoginPasswordRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Логин по паролю с JSON-телом.
    Поведение:
      - Успех без state: { ok:true, redirect_to:null } + установка SSO-cookie.
      - Успех с валидными state+client_id (pending в Redis): выдаём code, удаляем pending,
        возвращаем { ok:true, redirect_to:"<redirect_uri>?code=...&state=..." } + cookie.
    Ошибки: через HTTPException, их перехватит глобальный хендлер.
    """

    # 1) Rate limit
    await rate_limiter.check_rate_limit(request, "login", max_requests=10)

    # 2) Поиск пользователя и базовые проверки
    user = await user_crud.get_by_email(session, login_data.email)
    if not user:
        await rate_limiter.add_failed_attempt(login_data.email, "login")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not security.verify_password(login_data.password, user.password_hash):
        await user_crud.update_login_info(session, user, success=False)
        await rate_limiter.add_failed_attempt(login_data.email, "login")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Опциональная тихая пере-вычисляемость хэша
    if security.needs_rehash(user.password_hash):
        await user_crud.rehash_password(session, user, login_data.password)

    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email first")

    # 3) Успешный вход: аудит и очистка счётчиков
    await rate_limiter.clear_failed_attempts(login_data.email, "login")
    await user_crud.update_login_info(session, user, success=True)

    # 4) Создать IdP-сессию
    idp_session = await session_service.create_session(
        session=session,
        user=user,
        request=request,
        remember_me=login_data.remember_me,
    )
    # Вычислить max_age для куки из hard-max TTL сессии
    max_age = int((idp_session.max_expires_at - datetime.now(timezone.utc)).total_seconds())

    # 5) OIDC-продолжение, если пришли client_id+state и в Redis есть pending authreq
    redirect_to: Optional[str] = None
    if login_data.client_id and login_data.state and rate_limiter.redis_client:
        raw = await rate_limiter.redis_client.get(f"authreq:{login_data.state}")
        if raw:
            data = json.loads(raw)

            # Валидация клиента и redirect_uri
            client = await client_crud.get_by_client_id(session, login_data.client_id)
            if client and data.get("client_id") == login_data.client_id and validators.validate_redirect_uri(
                data.get("redirect_uri"), client.redirect_uris or []
            ):
                # Выпускаем одноразовый authorization code
                code = await token_service.create_auth_code(
                    session=session,
                    user=user,
                    client=client,
                    redirect_uri=data["redirect_uri"],
                    scope=data["scope"],
                    state=login_data.state,
                    nonce=data.get("nonce"),
                    code_challenge=data.get("code_challenge"),
                    ip_address=request.client.host,
                    user_agent=request.headers.get("User-Agent"),
                )

                # Привяжем sid к коду на TTL кода и удалим pending
                await rate_limiter.redis_client.setex(f"authcode_sid:{code}", settings.AUTH_CODE_TTL, idp_session.session_id)
                await rate_limiter.redis_client.delete(f"authreq:{login_data.state}")

                # Сформировать redirect_to строку для фронта
                params = {"code": code, "state": login_data.state}
                redirect_to = f'{data["redirect_uri"]}?{urlencode(params)}'

    # 6) Установить SSO-cookie на сам JSON-ответ
    session_service.set_session_cookie(response, idp_session.session_id, max_age=max_age)

    # 7) Вернуть унифицированный JSON-ответ без 302
    return LoginPasswordResponse(ok=True, message="Login successful", redirect_to=redirect_to)
