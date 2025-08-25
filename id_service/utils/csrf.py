# id_service/utils/csrf.py

import hmac
import hashlib
import secrets
from typing import Optional

from fastapi import Request, HTTPException, status


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
        submitted_token: Optional[str] = None,
    ) -> bool:
        """
        Validate CSRF token (double-submit: cookie vs header/form)
        Raises HTTPException(403) if invalid, returns True if valid.
        """

        # 1) token from cookie
        if cookie_token is None:
            cookie_token = request.cookies.get(self.cookie_name)

        if not cookie_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF cookie not found"
            )

        # 2) token from header (preferred) or form field (fallback)
        if submitted_token is None:
            submitted_token = request.headers.get(self.header_name)

            if not submitted_token and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
                try:
                    form = await request.form()
                    submitted_token = form.get(self.form_field)
                except Exception:
                    submitted_token = None

        if not submitted_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token not provided"
            )

        # 3) constant-time compare
        if not hmac.compare_digest(cookie_token, submitted_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token"
            )

        return True

    def should_check_csrf(self, request: Request) -> bool:
        """
        Decide if the current request must pass CSRF check.

        Safe methods are skipped. We explicitly *protect*:
        - /api/auth/**
        - /api/account/**
        - (на всякий случай совместимость с неполным префиксом)
          /auth/** и /account/**
        - /oauth/authorize**   (включая /oauth/authorize/consent)

        Exclusions:
        - /api/auth/csrf (и /auth/csrf)
        - /.well-known/*
        - /oauth/token, /oauth/revoke, а также корневые /token, /revoke
        - /health, /health/ready
        - Любые запросы с Authorization: Bearer*, КРОМЕ явных protected путей.
        """
        method = request.method.upper()
        if method in {"GET", "HEAD", "OPTIONS"}:
            return False

        path = request.url.path

        # --- explicit exclusions ---
        if path in {
            "/api/auth/csrf",
            "/auth/csrf",
            "/.well-known/openid-configuration",
            "/.well-known/jwks.json",
            "/health",
            "/health/ready",
            "/oauth/token",
            "/oauth/revoke",
            "/token",
            "/revoke",
        }:
            return False

        # --- explicit protected areas ---
        is_protected = (
            path.startswith("/api/auth/")
            or path.startswith("/api/account/")
            or path.startswith("/auth/")
            or path.startswith("/account/")
            or path.startswith("/oauth/authorize")  # covers /oauth/authorize/consent
            or path == "/logout"  # POST /logout гасит cookie-сессию — защищаем
        )
        if is_protected:
            return True

        # Bearer requests (API calls with JWT) usually don't need CSRF
        # (keep AFTER explicit protected check so consent stays protected)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return False

        # default
        return False


csrf_protection = CSRFProtection()
