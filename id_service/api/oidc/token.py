# id_service/api/oidc/token.py

import base64
import json
import logging
from typing import Optional, Tuple

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from utils.rate_limit import rate_limiter
from crud import client_crud
from models import TokenAuthMethod, ClientType, User
from services.token_service import token_service
from utils.validators import validators
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def _oauth_error(error: str, desc: str, status_code: int = 400):
    return JSONResponse(
        {"error": error, "error_description": desc},
        status_code=status_code,
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )

def _basic_auth(header: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not header or not header.lower().startswith("basic "):
        return None, None
    try:
        raw = base64.b64decode(header.split(" ", 1)[1]).decode()
        client_id, client_secret = raw.split(":", 1)
        return client_id, client_secret
    except Exception:
        return None, None


async def _get_client_and_auth(request: Request, session: AsyncSession, form_client_id: Optional[str], form_client_secret: Optional[str]):
    auth_header = request.headers.get("Authorization")
    basic_id, basic_secret = _basic_auth(auth_header)
    client_id = basic_id or form_client_id
    client = await client_crud.get_by_client_id(session, client_id) if client_id else None
    if not client:
        return None, _oauth_error("invalid_client", "Unknown client_id", 401)

    # Determine how client authenticates
    method = client.token_endpoint_auth_method
    if method == TokenAuthMethod.NONE:
        # public client, no secret expected
        return client, None
    elif method == TokenAuthMethod.CLIENT_SECRET_BASIC:
        if basic_id is None:
            return None, _oauth_error("invalid_client", "client_secret_basic required", 401)
        if not await client_crud.verify_secret(client, basic_secret or ""):
            return None, _oauth_error("invalid_client", "Invalid client secret", 401)
        return client, None
    elif method == TokenAuthMethod.CLIENT_SECRET_POST:
        secret = form_client_secret or ""
        if not await client_crud.verify_secret(client, secret):
            return None, _oauth_error("invalid_client", "Invalid client secret", 401)
        return client, None
    else:
        return None, _oauth_error("invalid_client", "Unsupported auth method", 401)


@router.post("/token")
async def token(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
):
    client, err = await _get_client_and_auth(request, session, client_id, client_secret)
    if err:
        return err

    if grant_type == "authorization_code":
        if not code or not redirect_uri:
            return _oauth_error("invalid_request", "code and redirect_uri are required")

        # PKCE: для public/required — обязателен корректный verifier
        require_pkce = client.type == ClientType.PUBLIC or (getattr(client, "pkce_required", True) is True)
        if require_pkce:
            ok, errtxt = validators.validate_pkce_verifier(code_verifier or "")
            if not ok:
                return _oauth_error("invalid_request", errtxt)

        auth_code, oauth_err = await token_service.exchange_auth_code(
            session=session,
            code=code,
            client_id=client.client_id,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )
        if oauth_err or not auth_code:
            return _oauth_error("invalid_grant", "invalid authorization code")

        # ЯВНО загружаем пользователя
        user = await session.get(User, auth_code.user_id)
        if not user:
            return _oauth_error("invalid_grant", "user not found")

        # Получаем sid из Redis (могут вернуться bytes -> декодируем)
        sid = None
        if rate_limiter.redis_client:
            sid = await rate_limiter.redis_client.get(f"authcode_sid:{code}")
            if isinstance(sid, (bytes, bytearray)):
                sid = sid.decode("utf-8")

        tokens = await token_service.create_tokens(
            session=session,
            user=user,
            client=client,
            scope=auth_code.scope,
            nonce=auth_code.nonce,
            auth_time=auth_code.auth_time,
            session_id=sid,
            ip_address=(request.client.host if request.client else None),
            user_agent=request.headers.get("User-Agent"),
        )

        return JSONResponse(tokens, headers={"Cache-Control": "no-store", "Pragma": "no-cache"})

    elif grant_type == "refresh_token":
        if not refresh_token:
            return _oauth_error("invalid_request", "refresh_token is required")

        new_tokens, oauth_err = await token_service.rotate_refresh_token(
            session=session,
            refresh_token=refresh_token,
            client_id=client.client_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent"),
        )
        if oauth_err:
            return _oauth_error(oauth_err, "cannot rotate refresh token")
        return JSONResponse(new_tokens, headers={"Cache-Control": "no-store", "Pragma": "no-cache"})


    else:
        return _oauth_error("unsupported_grant_type", "Only authorization_code and refresh_token are supported")
