# id_service/api/oidc/authorize.py

import json
import logging
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from core.config import settings
from crud import client_crud, user_crud
from services.session_service import session_service
from services.token_service import token_service
from utils.validators import validators
from utils.rate_limit import rate_limiter
from models import ClientType

logger = logging.getLogger(__name__)
router = APIRouter()


def _oauth_error_redirect(redirect_uri: Optional[str], state: Optional[str], error: str, desc: str):
    if redirect_uri:
        params = {"error": error, "error_description": desc}
        if state is not None:
            params["state"] = state
        return RedirectResponse(
            url=f"{redirect_uri}?{urlencode(params)}",
            status_code=302,
            headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
        )
    # Fallback: JSON вместо HTML
    body = {"error": error, "error_description": desc}
    if state is not None:
        body["state"] = state
    return JSONResponse(body, status_code=400, headers={"Cache-Control": "no-store", "Pragma": "no-cache"})


@router.get("/authorize")
async def authorize(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    client_id: str = Query(...),
    response_type: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(...),
    state: str = Query(..., min_length=1),
    nonce: Optional[str] = Query(None),
    code_challenge: Optional[str] = Query(None),
    code_challenge_method: Optional[str] = Query(None),
):
    # Базовая валидация запроса
    if response_type != "code":
        return _oauth_error_redirect(redirect_uri, state, "unsupported_response_type", "Only response_type=code is supported")

    client = await client_crud.get_by_client_id(session, client_id)
    if not client:
        return _oauth_error_redirect(redirect_uri, state, "unauthorized_client", "Unknown client_id")

    if not validators.validate_redirect_uri(redirect_uri, client.redirect_uris or []):
        return _oauth_error_redirect(redirect_uri, state, "invalid_request", "redirect_uri is not registered for client")

    ok, err = validators.validate_scope(scope)
    if not ok:
        return _oauth_error_redirect(redirect_uri, state, "invalid_scope", err)

    ok, err = validators.validate_state(state)
    if not ok:
        return _oauth_error_redirect(redirect_uri, state, "invalid_request", err)

    ok, err = validators.validate_nonce(nonce or "")
    if not ok:
        return _oauth_error_redirect(redirect_uri, state, "invalid_request", err)

    # PKCE требования
    require_pkce = client.type == ClientType.PUBLIC or (getattr(client, "pkce_required", True) is True)
    if require_pkce:
        if code_challenge is None or (code_challenge_method or "S256") != "S256":
            return _oauth_error_redirect(redirect_uri, state, "invalid_request", "PKCE S256 is required")

    # Если есть SSO — выдаем code и редиректим сразу
    idp_session = await session_service.get_session_from_cookie(session, request)
    if idp_session:
        user = await user_crud.get_by_id(session, idp_session.user_id)
        if not user:
            return _oauth_error_redirect(redirect_uri, state, "access_denied", "User not found")

        code = await token_service.create_auth_code(
            session=session,
            user=user,
            client=client,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            nonce=nonce,
            code_challenge=code_challenge,  # сохраняем как есть, верифицируем на /token
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent"),
        )

        # Привяжем sid к коду через Redis, чтобы потом добавить в id_token
        if rate_limiter.redis_client:
            await rate_limiter.redis_client.setex(
                f"authcode_sid:{code}", settings.AUTH_CODE_TTL, idp_session.session_id
            )

        params = {"code": code, "state": state}
        return RedirectResponse(url=f"{redirect_uri}?{urlencode(params)}", status_code=302)

    # Нет SSO — сохраним pending и редиректим на SPA /login
    if not rate_limiter.redis_client:
        return _oauth_error_redirect(redirect_uri, state, "server_error", "Redis unavailable")

    payload = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "created_at": "now",
        "ip": request.client.host,
        "ua": validators.sanitize_user_agent(request.headers.get("User-Agent")),
    }
    await rate_limiter.redis_client.setex(f"authreq:{state}", settings.AUTH_CODE_TTL, json.dumps(payload))

    # базовый origin текущего хоста (id.localhost или id.asynq.ru)
    host = request.headers.get("host") or request.url.netloc
    origin = f"{request.url.scheme}://{host.split(',')[0].strip()}"
    login_qs = urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        **({"nonce": nonce} if nonce else {}),
        **({"code_challenge": code_challenge} if code_challenge else {}),
    })
    return RedirectResponse(url=f"{origin}/login?{login_qs}", status_code=302)