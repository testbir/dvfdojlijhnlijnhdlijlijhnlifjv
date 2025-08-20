#id_service/api/oidc/logout.py

import logging
import asyncio 

from typing import Optional
from urllib.parse import urlencode
from fastapi import APIRouter, Request, Response, Depends, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from db.session import get_async_session
from services.session_service import session_service
from services.backchannel_logout import backchannel_logout_service
from services.jwk_service import jwk_service
from crud import client_crud, user_crud
from utils.validators import validators
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/logout")
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
    id_token_hint: Optional[str] = Query(None),
    post_logout_redirect_uri: Optional[str] = Query(None),
    state: Optional[str] = Query(None)
):
    """OpenID Connect RP-Initiated Logout endpoint"""
    
    client_id = None
    user = None
    
    # Parse id_token_hint to get client and user
    if id_token_hint:
        try:
            hdr = jwt.get_unverified_header(id_token_hint)
            kid = hdr.get("kid")
            jwk = await jwk_service.get_key_by_kid(kid) if kid else None
            if not jwk:
                raise JWTError("unknown kid")
            public_key = jwk_service.load_public_key(jwk.public_pem)

            # aud проверять не надо, это лишь hint для выбора клиента
            claims = jwt.decode(
                id_token_hint,
                public_key,
                algorithms=["RS256"],
                issuer=settings.ISSUER,
                options={"verify_aud": False}
            )

            client_id = claims.get("aud")
            user_id = claims.get("sub")
            if user_id:
                user = await user_crud.get_by_id(session, user_id)
        except JWTError:
            logger.warning("Invalid id_token_hint provided")
            client_id = None
            user = None
            
    # Get SSO session
    idp_session = await session_service.get_session_from_cookie(session, request)
    
    if idp_session:
        # Get user from session if not from token
        if not user:
            user = await user_crud.get_by_id(session, idp_session.user_id)
        
        # Revoke session
        await session_service.revoke_session(session, idp_session)
        
        # Clear session cookie
        session_service.clear_session_cookie(response)
        
        # Trigger back-channel logout
        if user:
            asyncio.create_task(
                backchannel_logout_service.initiate_backchannel_logout(
                    session=None,  # сервис сам откроет сессию
                    user=user,
                    session_id=idp_session.session_id,
                    reason="rp_logout",
                )
            )
    
    # Validate post logout redirect URI
    if post_logout_redirect_uri and client_id:
        client = await client_crud.get_by_client_id(session, client_id)
        if client and validators.validate_redirect_uri(
            post_logout_redirect_uri,
            client.post_logout_redirect_uris
        ):
            # Build redirect URL
            params = {}
            if state:
                params["state"] = state
            
            redirect_url = post_logout_redirect_uri
            if params:
                redirect_url = f"{redirect_url}?{urlencode(params)}"
            
            return RedirectResponse(url=redirect_url, status_code=302)
    
    # Show logout confirmation page
    return _render_logout_page()


def _render_logout_page() -> HTMLResponse:
    """Render logout confirmation page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Выход - Asynq ID</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                padding: 40px;
                text-align: center;
                max-width: 400px;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                margin-bottom: 30px;
            }
            .icon {
                font-size: 48px;
                margin-bottom: 20px;
            }
            a {
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">✓</div>
            <h1>Вы вышли из системы</h1>
            <p>Вы успешно вышли из всех приложений Asynq.</p>
            <a href="/">На главную</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


