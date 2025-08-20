# id_service/api/oidc/discovery.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from core.config import settings
from schemas.oidc import DiscoveryResponse

router = APIRouter()


@router.get("/.well-known/openid-configuration", response_model=DiscoveryResponse)
async def openid_configuration(request: Request):
    """OpenID Connect Discovery endpoint"""
    
    base_url = settings.ISSUER
    
    return DiscoveryResponse(
        issuer=base_url,
        authorization_endpoint=f"{base_url}/authorize",
        token_endpoint=f"{base_url}/token",
        userinfo_endpoint=f"{base_url}/userinfo",
        jwks_uri=f"{base_url}/.well-known/jwks.json",
        end_session_endpoint=f"{base_url}/logout",
        response_types_supported=["code"],
        grant_types_supported=["authorization_code", "refresh_token"],
        scopes_supported=["openid", "email", "profile", "offline_access"],
        id_token_signing_alg_values_supported=["RS256"],
        subject_types_supported=["public"],
        token_endpoint_auth_methods_supported=["none", "client_secret_post", "client_secret_basic"],
        code_challenge_methods_supported=["S256"],
        claims_supported=[
            "sub", "email", "email_verified", "preferred_username",
            "auth_time", "iss", "aud", "exp", "iat", "nonce", "at_hash", "sid"
        ],
        frontchannel_logout_supported=True,
        backchannel_logout_supported=True,
        backchannel_logout_session_supported=True
    )