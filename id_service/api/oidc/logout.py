# id_service/api/oidc/logout.py
"""
OIDC RP-Initiated Logout.

Изменения:
- Добавлен JSON-логаут: POST /logout с телом LogoutRequest и ответом LogoutResponse.
- GET /logout упрощён: больше НЕТ HTML/iframes. Только:
    - 302 на валидный post_logout_redirect_uri (если он валиден для клиента из id_token_hint)
    - иначе 204 No Content.
- Back-channel остаётся. Фронт-канал удалён.
- Очистка cookie и отзыв IdP-сессии — только в POST-варианте (по ТЗ).
"""

import logging
import asyncio
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Request, Response, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from db.session import get_async_session
from services.session_service import session_service
from services.backchannel_logout import backchannel_logout_service
from services.jwk_service import jwk_service
from crud import client_crud, user_crud
from utils.validators import validators
from core.config import settings
from schemas.oidc import LogoutRequest, LogoutResponse

logger = logging.getLogger(__name__)
router = APIRouter()


async def _parse_id_token_hint(
    id_token_hint: Optional[str],
    session: AsyncSession,
) -> tuple[Optional[str], Optional[str]]:
    """
    Разбор id_token_hint.
    Возвращает (client_id, user_id) если токен корректен. Иначе (None, None).
    Аудиторию (aud) валидируем как строку одного клиента.
    """
    if not id_token_hint:
        return None, None
    try:
        hdr = jwt.get_unverified_header(id_token_hint)
        kid = hdr.get("kid")
        jwk = await jwk_service.get_key_by_kid(kid) if kid else None
        if not jwk:
            raise JWTError("unknown kid")
        public_key = jwk_service.load_public_key(jwk.public_pem)

        # aud проверять как hint: verify_aud=False, но issuer проверяем
        claims = jwt.decode(
            id_token_hint,
            public_key,
            algorithms=["RS256"],
            issuer=settings.ISSUER,
            options={"verify_aud": False},
        )
        aud = claims.get("aud")
        client_id = aud if isinstance(aud, str) else None
        user_id = claims.get("sub")
        return client_id, user_id
    except JWTError:
        logger.warning("Invalid id_token_hint provided")
        return None, None


def _build_redirect(redirect_uri: Optional[str], state: Optional[str]) -> Optional[str]:
    """Собирает redirect_to строку с ?state=... если задано."""
    if not redirect_uri:
        return None
    if state:
        return f"{redirect_uri}?{urlencode({'state': state})}"
    return redirect_uri


@router.post("/logout", response_model=LogoutResponse)
async def logout_post(
    request: Request,
    response: Response,
    body: LogoutRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    JSON-логаут.
    Действия:
      - Если есть IdP-сессия: отозвать, очистить cookie, дернуть back-channel.
      - Валидация post_logout_redirect_uri идёт по клиенту из id_token_hint.
      - Возвращаем { ok: true, redirect_to: <uri>|null }. 302 нет.
    """
    # 1) Разобрать id_token_hint, чтобы понять клиента и пользователя (для back-channel)
    client_id_from_hint, user_id_from_hint = await _parse_id_token_hint(body.id_token_hint, session)

    # 2) Считать текущую IdP-сессию из cookie
    idp_session = await session_service.get_session_from_cookie(session, request)
    current_user = None

    # 3) Если сессия есть — отзываем и очищаем cookie
    if idp_session:
        # Если пользователя ещё не знаем — загрузим
        if not user_id_from_hint:
            user_id_from_hint = str(idp_session.user_id)
        current_user = await user_crud.get_by_id(session, user_id_from_hint) if user_id_from_hint else None

        await session_service.revoke_session(session, idp_session)
        session_service.clear_session_cookie(response)

        # 4) Back-channel для активных RP (как раньше)
        if current_user:
            asyncio.create_task(
                backchannel_logout_service.initiate_backchannel_logout(
                    session=None,  # сервис сам откроет сессию
                    user=current_user,
                    session_id=idp_session.session_id,
                    reason="rp_logout",
                )
            )

    # 5) Валидация post_logout_redirect_uri по клиенту из id_token_hint
    redirect_to: Optional[str] = None
    if body.post_logout_redirect_uri and client_id_from_hint:
        client = await client_crud.get_by_client_id(session, client_id_from_hint)
        if client and validators.validate_redirect_uri(body.post_logout_redirect_uri, client.post_logout_redirect_uris):
            redirect_to = _build_redirect(body.post_logout_redirect_uri, body.state)

    # 6) JSON-ответ
    return LogoutResponse(ok=True, redirect_to=redirect_to)


@router.get("/logout")
async def logout_get(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    id_token_hint: Optional[str] = Query(None),
    post_logout_redirect_uri: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
):
    """
    Упрощённый GET-вариант.
    Никаких HTML/iframes. Без очистки cookie и без ревокации.
    Если redirect валиден по клиенту из id_token_hint — 302 туда (добавим state).
    Иначе — 204 No Content.
    """
    client_id_from_hint, _ = await _parse_id_token_hint(id_token_hint, session)

    if post_logout_redirect_uri and client_id_from_hint:
        client = await client_crud.get_by_client_id(session, client_id_from_hint)
        if client and validators.validate_redirect_uri(post_logout_redirect_uri, client.post_logout_redirect_uris):
            url = _build_redirect(post_logout_redirect_uri, state)
            return RedirectResponse(url=url, status_code=302)

    # Ничего не делаем, даём 204
    return Response(status_code=204)
