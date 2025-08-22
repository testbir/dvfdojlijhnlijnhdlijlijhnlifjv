# id_service/core/security.py

import base64
import hashlib
import hmac
import secrets
import string
from typing import Tuple

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError
from core.config import settings


class SecurityService:

    def __init__(self) -> None:
        self.pepper = settings.PEPPER_SECRET
        self.ph = PasswordHasher(
            time_cost=settings.ARGON2_TIME_COST,
            memory_cost=settings.ARGON2_MEMORY_COST,
            parallelism=settings.ARGON2_PARALLELISM,
            hash_len=settings.ARGON2_HASH_LEN,
            salt_len=settings.ARGON2_SALT_LEN,
            type=Type.ID,
        )
    # -------- Password hashing (Argon2id + pepper) --------
    def hash_password(self, password: str) -> str:
        return self.ph.hash(f"{password}{self.pepper}")

    def is_argon2id_hash(self, stored: str) -> bool:
        return stored.startswith("$argon2id$")


    def verify_password(self, password: str, stored: str) -> bool:
        if not self.is_argon2id_hash(stored):
            return False
        try:
            self.ph.verify(stored, f"{password}{self.pepper}")
            return True
        except VerifyMismatchError:
            return False
        except Exception:
            return False

    def needs_rehash(self, stored: str) -> bool:
        if not self.is_argon2id_hash(stored):
            return False
        try:
            return self.ph.check_needs_rehash(stored)
        except Exception:
            return True

    # -------- OTP (email codes) --------
    def generate_otp(self, length: int = 4) -> str:
        digits = string.digits
        return "".join(secrets.choice(digits) for _ in range(length))

    def hash_otp(self, code: str) -> str:
        digest = hmac.new(self.pepper.encode("utf-8"), code.encode("utf-8"), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")

    def constant_time_compare(self, a: str, b: str) -> bool:
        return hmac.compare_digest(a, b)

    # -------- Password policy --------
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        if len(password) < int(getattr(settings, "PASSWORD_MIN_LENGTH", 8)):
            return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
        if getattr(settings, "PASSWORD_REQUIRE_UPPERCASE", True) and not any(c.isupper() for c in password):
            return False, "Password must contain an uppercase letter"
        if getattr(settings, "PASSWORD_REQUIRE_LOWERCASE", True) and not any(c.islower() for c in password):
            return False, "Password must contain a lowercase letter"
        if getattr(settings, "PASSWORD_REQUIRE_DIGIT", True) and not any(c.isdigit() for c in password):
            return False, "Password must contain a digit"
        if getattr(settings, "PASSWORD_REQUIRE_SPECIAL", False) and not any(c in "!@#$%^&*()-_=+[]{};:,.?/\\|" for c in password):
            return False, "Password must contain a special character"
        return True, ""

    # -------- PKCE S256 --------
    def verify_code_challenge(self, code_verifier: str, stored_challenge: str) -> bool:
        if not code_verifier or not stored_challenge:
            return False
        if len(code_verifier) < 43 or len(code_verifier) > 128:
            return False
        allowed = set(string.ascii_letters + string.digits + "-._~")
        if any(c not in allowed for c in code_verifier):
            return False
        digest = hashlib.sha256(code_verifier.encode()).digest()
        computed = base64.urlsafe_b64encode(digest).decode().rstrip("=")
        return hmac.compare_digest(computed, stored_challenge)


security = SecurityService()
