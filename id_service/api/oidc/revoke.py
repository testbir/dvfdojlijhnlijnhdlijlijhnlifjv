# id_service/api/oidc/revoke.py

import logging
from typing import Optional

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from .token import _get_client_and_auth  # используем тот же helper
from services.token_service import token_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/revoke")
async def revoke(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
):
    # Аутентифицируем клиента так же, как на /token
    client, err = await _get_client_and_auth(request, session, client_id, client_secret)
    if err:
        return err  # 401 invalid_client при ошибке

    # Поддерживаем только refresh_token (access — самодостаточный JWT)
    if token_type_hint and token_type_hint not in ("refresh_token", "access_token"):
        # по RFC просто игнорируем hint и продолжаем
        pass

    # По RFC: всегда 200 OK даже если токен невалиден/не найден
    try:
        await token_service.revoke_refresh_token(
            session=session,
            refresh_token=token,
            client_id=client.client_id,
            reason="revoked_by_client",
        )
    except Exception:
        # не палим детали наружу
        pass

    return JSONResponse({}, status_code=200, headers={"Cache-Control": "no-store", "Pragma": "no-cache"})
