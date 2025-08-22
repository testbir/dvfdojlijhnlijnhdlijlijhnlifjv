# id_service/utils/csrf.py

import hmac
import hashlib
import secrets
from typing import Optional
from fastapi import Depends, Request, HTTPException, status

from core.config import settings


class CSRFProtection:
    """CSRF protection using double-submit cookie pattern"""
    
    def __init__(self):
        self.cookie_name = "csrf_token"
        self.header_name = "X-CSRF-Token"
        self.form_field = "csrf_token"
    
    def generate_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    async def validate_token(
        self,
        request: Request,
        cookie_token: Optional[str] = None,
        submitted_token: Optional[str] = None
    ) -> bool:
        """
        Validate CSRF token
        
        Args:
            request: FastAPI request
            cookie_token: Token from cookie (if not in request)
            submitted_token: Token from header/form (if not in request)
            
        Returns:
            True if valid, raises HTTPException if invalid
        """
        
        
        # Get token from cookie
        if cookie_token is None:
            cookie_token = request.cookies.get(self.cookie_name)

        if not cookie_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF cookie not found")

        if submitted_token is None:
            submitted_token = request.headers.get(self.header_name)

            if not submitted_token and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
                try:
                    form = await request.form()
                    submitted_token = form.get(self.form_field)
                except Exception:
                    submitted_token = None

        if not submitted_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token not provided")

        if not hmac.compare_digest(cookie_token, submitted_token):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")

        return True
    
    def should_check_csrf(self, request: Request) -> bool:
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return False
        path = request.url.path
        if path in {
            "/token", "/revoke", "/auth/csrf",
            "/.well-known/openid-configuration", "/.well-known/jwks.json",
            "/health", "/health/ready",
        }:
            return False
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return False
        return True



csrf_protection = CSRFProtection()