# id_service/schemas/oidc.py
"""
Схемы (Pydantic v2) для OIDC.
Важно:
- /oidc/logout теперь имеет JSON-вариант (POST) с телом/ответом ниже.
- /oidc/token и /oidc/revoke остаются RFC-совместимыми и свои ошибки формируют сами.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------
# OIDC Discovery
# ---------------------------

class DiscoveryResponse(BaseModel):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    jwks_uri: str
    end_session_endpoint: str

    response_types_supported: List[str]
    grant_types_supported: List[str]
    scopes_supported: List[str]
    id_token_signing_alg_values_supported: List[str]
    subject_types_supported: List[str]
    token_endpoint_auth_methods_supported: List[str]
    code_challenge_methods_supported: List[str]
    claims_supported: List[str]

    frontchannel_logout_supported: bool
    backchannel_logout_supported: bool
    backchannel_logout_session_supported: bool


# ---------------------------
# UserInfo
# ---------------------------

class UserInfoResponse(BaseModel):
    sub: str
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    preferred_username: Optional[str] = None
    updated_at: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# RP-Initiated Logout (JSON)
# ---------------------------

class LogoutRequest(BaseModel):
    """JSON-запрос на логаут по OIDC.
    Примечание: post_logout_redirect_uri валидируется по клиенту из id_token_hint.
    """
    id_token_hint: Optional[str] = Field(
        default=None,
        description="ID Token пользователя для определения клиента и валидации post_logout_redirect_uri"
    )
    post_logout_redirect_uri: Optional[str] = Field(
        default=None,
        description="Куда редиректить после логаута, если валиден для клиента"
    )
    state: Optional[str] = Field(
        default=None,
        description="Опциональное состояние, вернётся как параметр в redirect_to"
    )


class LogoutResponse(BaseModel):
    """JSON-ответ логаута.
    redirect_to: абсолютный URL или null. Фронт сам выполнит переход, 302 нет.
    """
    ok: bool = True
    redirect_to: Optional[str] = None
