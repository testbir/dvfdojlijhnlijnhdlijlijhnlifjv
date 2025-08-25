# id_service/services/token_service.py

import secrets
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple

from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import noload
from cryptography.hazmat.primitives import serialization

from db.session import async_session_maker
from models import AuthCode, RefreshToken, User, Client, JWKKey
from core.config import settings
from core.security import security
from services.jwk_service import jwk_service
from services.backchannel_logout import backchannel_logout_service
from services.session_service import session_service

logger = logging.getLogger(__name__)


def _load_public_key(pem: str):
    """Загрузка публичного ключа из PEM."""
    return serialization.load_pem_public_key(pem.encode("utf-8"))


class TokenService:
    """Service for managing OAuth2/OIDC tokens"""

    async def create_auth_code(
        self,
        session: AsyncSession,
        user: User,
        client: Client,
        redirect_uri: str,
        scope: str,
        state: Optional[str] = None,
        nonce: Optional[str] = None,
        code_challenge: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """
        Создать одноразовый authorization code с биндингами (PKCE, redirect_uri, scope, nonce, state).
        Храним только sha256 от кода.
        """
        code = secrets.token_urlsafe(32)
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        now = datetime.now(timezone.utc)

        code_challenge_hash = code_challenge
        
        auth_code = AuthCode(
            code_hash=code_hash,
            client_id=client.client_id,
            user_id=user.id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge_hash=code_challenge_hash,
            nonce=nonce,
            state=state,
            auth_time=now,
            expires_at=now + timedelta(seconds=settings.AUTH_CODE_TTL),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session.add(auth_code)
        await session.flush()
        return code

    async def exchange_auth_code(
        self,
        session: AsyncSession,
        code: str,
        client_id: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> Tuple[Optional[AuthCode], Optional[str]]:
        """
        Обмен authorization code → проверка срока, one-time, PKCE и биндингов.
        Возвращает найденный AuthCode или ошибку OAuth.
        """
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        now = datetime.now(timezone.utc)

        result = await session.execute(
            select(AuthCode)
            .options(noload("*"))                      # отключаем eager-join всех связей
            .where(
                and_(
                    AuthCode.code_hash == code_hash,
                    AuthCode.client_id == client_id,
                    AuthCode.redirect_uri == redirect_uri,
                    AuthCode.expires_at > now,
                    AuthCode.used_at.is_(None),
                )
            )
            .with_for_update(of=AuthCode)              # блокируем только auth_codes
        )
        auth_code = result.scalar_one_or_none()
        if not auth_code:
            logger.warning("Invalid code exchange. client_id=%s", client_id)
            return None, "invalid_grant"

        # PKCE проверяем, если был челендж
        if auth_code.code_challenge_hash:
            if not code_verifier:
                return None, "invalid_request"
            if not security.verify_code_challenge(code_verifier, auth_code.code_challenge_hash):
                logger.warning("PKCE failed. client_id=%s", client_id)
                return None, "invalid_grant"

        # помечаем код использованным в транзакции
        auth_code.used_at = now
        await session.flush()
        return auth_code, None

    async def create_tokens(
        self,
        session: AsyncSession,
        user: User,
        client: Client,
        scope: str,
        nonce: Optional[str] = None,
        auth_time: Optional[datetime] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Выпуск access/id/refresh токенов.
        RS256 с текущим активным ключом. exp/iat — unix time.
        """
        now = datetime.now(timezone.utc)
        auth_time = auth_time or now
        ts = lambda dt: int(dt.timestamp())
        scopes = set(scope.split())

        # активный JWK
        jwk_key = await jwk_service.get_active_key()
        if not jwk_key:
            raise RuntimeError("No active JWK key available")

        private_key_pem = jwk_service.decrypt_private_key(jwk_key.private_pem_encrypted)

        # jti
        access_jti = secrets.token_urlsafe(16)
        refresh_jti = secrets.token_urlsafe(16)

        # access token
        access_claims = {
            "iss": settings.ISSUER,
            "sub": str(user.id),
            "aud": client.client_id,
            "exp": ts(now + timedelta(seconds=settings.ACCESS_TOKEN_TTL)),
            "iat": ts(now),
            "jti": access_jti,
            "scope": scope,
            "client_id": client.client_id,
        }
        if session_id:
            access_claims["sid"] = session_id

        access_token = jwt.encode(
            access_claims,
            private_key_pem,
            algorithm="RS256",
            headers={"kid": jwk_key.kid},
        )

        # id token при scope openid
        id_token: Optional[str] = None
        if "openid" in scopes:
            id_claims = {
                "iss": settings.ISSUER,
                "sub": str(user.id),
                "aud": client.client_id,
                "exp": ts(now + timedelta(seconds=settings.ACCESS_TOKEN_TTL)),
                "iat": ts(now),
                "auth_time": ts(auth_time),
            }
            if "email" in scopes:
                id_claims["email"] = user.email
                id_claims["email_verified"] = user.email_verified
            if "profile" in scopes:
                id_claims["preferred_username"] = user.username
            if nonce:
                id_claims["nonce"] = nonce
            if session_id:
                id_claims["sid"] = session_id

            # at_hash = left-most 128 bits of SHA-256(access_token), base64url без '='
            at_hash = hashlib.sha256(access_token.encode()).digest()[:16]
            import base64
            id_claims["at_hash"] = base64.urlsafe_b64encode(at_hash).decode().rstrip("=")

            id_token = jwt.encode(
                id_claims,
                private_key_pem,
                algorithm="RS256",
                headers={"kid": jwk_key.kid},
            )


        # refresh при offline_access
        refresh_token: Optional[str] = None
        if "offline_access" in scopes:
            refresh_token_obj = RefreshToken(
                jti=refresh_jti,
                user_id=user.id,
                client_id=client.client_id,
                scope=scope,
                created_at=now,
                expires_at=now + timedelta(seconds=settings.REFRESH_TOKEN_TTL),
                ip_address=ip_address,
                user_agent=user_agent,
            )
            session.add(refresh_token_obj)
            await session.flush()

            refresh_claims = {
                "iss": settings.ISSUER,
                "sub": str(user.id),
                "aud": client.client_id,
                "exp": ts(now + timedelta(seconds=settings.REFRESH_TOKEN_TTL)),
                "iat": ts(now),
                "jti": refresh_jti,
                "scope": scope,
                "token_type": "refresh",
            }
            refresh_token = jwt.encode(
                refresh_claims,
                private_key_pem,
                algorithm="RS256",
                headers={"kid": jwk_key.kid},
            )

        return {
            "access_token": access_token,
            "id_token": id_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_TTL,
            "scope": scope,
        }

    async def rotate_refresh_token(
        self,
        session: AsyncSession,
        refresh_token: str,
        client_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            unverified = jwt.get_unverified_header(refresh_token)
            kid = unverified.get("kid")
            if not kid:
                return None, "invalid_grant"

            # Берём ключ по kid
            result = await session.execute(select(JWKKey).where(JWKKey.kid == kid))
            jwk_key = result.scalar_one_or_none()
            if not jwk_key:
                return None, "invalid_grant"

            # Верифицируем токен
            private_key_pem = jwk_service.decrypt_private_key(jwk_key.private_pem_encrypted)
            claims = jwt.decode(
                refresh_token,
                private_key_pem,  # допустимо, ключ RSA приватный содержит публичную часть
                algorithms=["RS256"],
                audience=client_id,
                issuer=settings.ISSUER,
            )
            if claims.get("token_type") != "refresh":
                return None, "invalid_grant"

            jti = claims.get("jti")
            user_id = claims.get("sub")

            # Лочим запись рефреша
            result = await session.execute(
                select(RefreshToken)
                .where(
                    and_(
                        RefreshToken.jti == jti,
                        RefreshToken.client_id == client_id,
                        RefreshToken.revoked_at.is_(None),
                    )
                )
                .with_for_update()
            )
            refresh_token_obj = result.scalar_one_or_none()

            if not refresh_token_obj:
                # Проверка reuse
                result = await session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
                used_token = result.scalar_one_or_none()
                if used_token:
                    logger.critical("Refresh reuse detected. user_id=%s client_id=%s", user_id, client_id)
                    await self._revoke_token_chain(session, used_token)
                    return None, "invalid_grant"
                return None, "invalid_grant"

            now = datetime.now(timezone.utc)

            # Протух
            if refresh_token_obj.expires_at < now:
                refresh_token_obj.revoked_at = now
                refresh_token_obj.revoked_reason = "expired"
                await session.flush()
                return None, "invalid_grant"

            # Получаем сущности корректно
            user = await session.get(User, user_id)
            # ВАЖНО: Client ищем по client_id, а не по PK
            cres = await session.execute(select(Client).where(Client.client_id == client_id))
            client = cres.scalar_one_or_none()
            if not user or not client:
                return None, "invalid_grant"

            # Жёсткая ротация: старый сразу недействителен
            refresh_token_obj.rotated_at = now
            refresh_token_obj.revoked_at = now
            refresh_token_obj.revoked_reason = "rotated"


            # Выпускаем новую пачку
            new_tokens = await self.create_tokens(
                session=session,
                user=user,
                client=client,
                scope=refresh_token_obj.scope,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            # Связываем цепочку
            if new_tokens.get("refresh_token"):
                try:
                    new_jti = jwt.get_unverified_claims(new_tokens["refresh_token"]).get("jti")
                except Exception:
                    new_jti = None
                res2 = await session.execute(select(RefreshToken).where(RefreshToken.jti == new_jti))
                new_refresh_obj = res2.scalar_one()
                new_refresh_obj.parent_jti = refresh_token_obj.jti
                new_refresh_obj.prev_jti = refresh_token_obj.jti

            await session.flush()
            return new_tokens, None

        except JWTError as e:
            logger.warning("JWT error during refresh: %s", e)
            return None, "invalid_grant"
        except Exception as e:
            logger.error("Error rotating refresh token: %s", e)
            return None, "server_error"

    async def revoke_refresh_token(
        self,
        session: AsyncSession,
        refresh_token: str,
        client_id: str,
        reason: str = "revoked_by_client",
    ) -> None:
        """
        RFC 7009: отзыв refresh токена. Безболезненно возвращает 200 даже если токен невалиден.
        Мы отзывем сам токен и всех его потомков по цепочке parent_jti.
        """
        try:
            # Вычисляем ключ по kid и валидируем токен
            unverified = jwt.get_unverified_header(refresh_token)
            kid = unverified.get("kid")
            if not kid:
                return

            res = await session.execute(select(JWKKey).where(JWKKey.kid == kid))
            jwk_key = res.scalar_one_or_none()
            if not jwk_key:
                return

            private_key_pem = jwk_service.decrypt_private_key(jwk_key.private_pem_encrypted)
            claims = jwt.decode(
                refresh_token,
                private_key_pem,  # валидно: приватный ключ содержит публичную часть
                algorithms=["RS256"],
                audience=client_id,
                issuer=settings.ISSUER,
            )
            jti = claims.get("jti")
            if not jti:
                return

            # Находим сам токен
            result = await session.execute(
                select(RefreshToken)
                .where(
                    and_(
                        RefreshToken.jti == jti,
                        RefreshToken.client_id == client_id,
                    )
                )
                .with_for_update(of=RefreshToken)
            )
            root = result.scalar_one_or_none()
            if not root:
                return

            now = datetime.now(timezone.utc)

            # Собираем всех потомков (широкий поиск по parent_jti)
            to_revoke = [root]
            queue = [root.jti]
            seen = set([root.jti])
            while queue:
                cur = queue.pop(0)
                res = await session.execute(select(RefreshToken).where(RefreshToken.parent_jti == cur))
                children = res.scalars().all()
                for c in children:
                    if c.jti not in seen:
                        seen.add(c.jti)
                        to_revoke.append(c)
                        queue.append(c.jti)

            # Отзываем
            for t in to_revoke:
                if not t.revoked_at:
                    t.revoked_at = now
                    t.revoked_reason = reason

            await session.flush()

        except JWTError:
            return
        except Exception:
            logger.exception("Error during refresh token revocation")
            return


    async def _revoke_token_chain(self, session: AsyncSession, token: RefreshToken) -> None:
        """
        Отозвать всю цепочку refresh при reuse. Плюс SSO и back-channel для соответствующего клиента.
        """
        now = datetime.now(timezone.utc)

        # собираем всю цепочку вверх по parent_jti
        tokens_to_revoke = []
        current = token
        while current.parent_jti:
            result = await session.execute(select(RefreshToken).where(RefreshToken.jti == current.parent_jti))
            parent = result.scalar_one_or_none()
            if parent:
                tokens_to_revoke.append(parent)
                current = parent
            else:
                break

        # и вниз по потомкам
        result = await session.execute(select(RefreshToken).where(RefreshToken.parent_jti == token.jti))
        children = result.scalars().all()
        tokens_to_revoke.extend(children)

        tokens_to_revoke.append(token)
        for t in tokens_to_revoke:
            if not t.revoked_at:
                t.revoked_at = now
                t.revoked_reason = "token_reuse_detected"
        await session.flush()

        # отзывает все IdP-сессии пользователя (пока глобально)
        await session_service.revoke_all_user_sessions(session, token.user_id)

        # back-channel точечно по клиенту токена
        user = await session.get(User, token.user_id)
        try:
            await backchannel_logout_service.initiate_backchannel_logout(
                session=session,
                user=user,
                session_id=None,
                reason="refresh_reuse",
                only_client_id=token.client_id,
            )
        except Exception as e:
            logger.error("Back-channel during revoke chain failed: %s", e)

    async def verify_access_token(
        self,
        token: str,
        required_scope: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Верификация access: подпись, iss. aud опционально. Проверка требуемого scope.
        """
        try:
            hdr = jwt.get_unverified_header(token)
            kid = hdr.get("kid")
            async with async_session_maker() as s:
                res = await s.execute(select(JWKKey).where(JWKKey.kid == kid))
                jwk_key = res.scalar_one_or_none()
                if not jwk_key:
                    return None
                public_key = _load_public_key(jwk_key.public_pem)
                claims = jwt.decode(
                    token,
                    public_key,
                    algorithms=["RS256"],
                    issuer=settings.ISSUER,
                    options={"verify_aud": False},
                )
            if required_scope and required_scope not in claims.get("scope", "").split():
                return None
            return claims
        except JWTError:
            return None

    async def revoke_all_refresh_tokens_for_user(
        self,
        session: AsyncSession,
        user_id: str,
        client_id: Optional[str] = None,
        reason: str = "user_action",
    ) -> list[str]:
        """
        Отозвать все активные refresh токены пользователя.
        Возвращает список client_id, у которых были активные токены.
        """
        now = datetime.now(timezone.utc)
        q = select(RefreshToken).where(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
        )
        if client_id:
            q = q.where(RefreshToken.client_id == client_id)

        res = await session.execute(q)
        tokens = res.scalars().all()

        affected = set()
        for t in tokens:
            t.revoked_at = now
            t.revoked_reason = reason
            affected.add(t.client_id)

        await session.flush()
        return list(affected)


token_service = TokenService()
