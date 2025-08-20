# id_service/services/jwk_service.py

import json
import base64
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from models import JWKKey
from core.config import settings
from db.session import async_session_maker

logger = logging.getLogger(__name__)


class JWKService:
    """Service for managing JSON Web Keys"""
    
    def __init__(self):
        # Create encryption key from settings
        key = base64.urlsafe_b64encode(settings.JWT_PRIVATE_KEY_PASSWORD.encode()[:32].ljust(32, b'0'))
        self.cipher = Fernet(key)
    
    async def ensure_active_key(self) -> JWKKey:
        """Ensure there's an active JWK key, create if not exists"""
        async with async_session_maker() as session:
            # Check for active key
            result = await session.execute(
                select(JWKKey).where(JWKKey.active == True)
            )
            active_key = result.scalar_one_or_none()
            
            if not active_key:
                logger.info("No active JWK key found, generating new one...")
                active_key = await self.generate_new_key(session)
                await session.commit()
            
            return active_key
    
    async def generate_new_key(self, session: AsyncSession) -> JWKKey:
        """Generate new RSA key pair"""
        # Generate RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Get PEM representations
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Encrypt private key
        encrypted_private = self.cipher.encrypt(private_pem)
        
        # Generate kid
        import secrets
        kid = secrets.token_urlsafe(16)
        
        # Create key record
        jwk_key = JWKKey(
            kid=kid,
            alg="RS256",
            public_pem=public_pem.decode('utf-8'),
            private_pem_encrypted=encrypted_private.decode('utf-8'),
            active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        # Deactivate old keys
        await session.execute(
            select(JWKKey).where(JWKKey.active == True).with_for_update()
        )
        result = await session.execute(
            select(JWKKey).where(JWKKey.active == True)
        )
        old_keys = result.scalars().all()
        for old_key in old_keys:
            old_key.active = False
            old_key.rotated_at = datetime.now(timezone.utc)
        
        session.add(jwk_key)
        return jwk_key
    
    async def get_active_key(self) -> Optional[JWKKey]:
        """Get current active key"""
        async with async_session_maker() as session:
            result = await session.execute(
                select(JWKKey).where(JWKKey.active == True)
            )
            return result.scalar_one_or_none()
    
    async def get_jwks(self) -> Dict[str, Any]:
        async with async_session_maker() as session:
            # держим предыдущие ключи минимум до истечения access/id токенов
            retention = timedelta(seconds=settings.ACCESS_TOKEN_TTL)
            cutoff = datetime.now(timezone.utc) - retention

            res = await session.execute(
                select(JWKKey).where(
                    or_(
                        JWKKey.active == True,
                        JWKKey.rotated_at >= cutoff
                    )
                )
            )
            keys = res.scalars().all()

            jwks = {"keys": []}
            for key in keys:
                public_key = serialization.load_pem_public_key(
                    key.public_pem.encode("utf-8"),
                    backend=default_backend()
                )
                numbers = public_key.public_numbers()
                def b64u(n: int) -> str:
                    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
                    return base64.urlsafe_b64encode(b).decode().rstrip("=")
                jwks["keys"].append({
                    "kty": "RSA",
                    "use": "sig",
                    "kid": key.kid,
                    "alg": key.alg,
                    "n": b64u(numbers.n),
                    "e": b64u(numbers.e),
                })
            return jwks
        
    def decrypt_private_key(self, encrypted_pem: str) -> bytes:
        """Decrypt private key"""
        return self.cipher.decrypt(encrypted_pem.encode('utf-8'))

    async def get_key_by_kid(self, kid: str) -> Optional[JWKKey]:
        async with async_session_maker() as session:
            res = await session.execute(select(JWKKey).where(JWKKey.kid == kid))
            return res.scalar_one_or_none()
        
    
    def load_public_key(self, public_pem: str):
        return serialization.load_pem_public_key(public_pem.encode("utf-8"))

jwk_service = JWKService()