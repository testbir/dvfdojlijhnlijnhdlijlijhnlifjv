# id_service/api/oidc/jwks.py

import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.jwk_service import jwk_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/.well-known/jwks.json")
async def jwks():
    jwks_dict = await jwk_service.get_jwks()
    return JSONResponse(
        jwks_dict,
        headers={
            "Cache-Control": "public, max-age=300, must-revalidate",
            "Content-Type": "application/json",
        },
    )
