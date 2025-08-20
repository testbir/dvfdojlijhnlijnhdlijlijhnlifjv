# id_service/utils/rate_limit.py

import hashlib
import logging
from typing import Optional
from fastapi import Request, HTTPException, status
import redis.asyncio as redis
from datetime import timedelta

from core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting implementation using Redis"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.RATE_LIMIT_ENABLED
        
    async def init(self):
        """Initialize Redis connection"""
        if self.enabled:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info("Rate limiter initialized")
            except Exception as e:
                logger.error(f"Failed to initialize rate limiter: {e}")
                self.enabled = False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _get_key(self, request: Request, action: str) -> str:
        """Generate rate limit key"""
        client_ip = request.client.host
        # Include action in key for different limits per action
        raw_key = f"rate_limit:{action}:{client_ip}"
        # Hash for privacy
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    async def check_rate_limit(
        self,
        request: Request,
        action: str = "general",
        max_requests: Optional[int] = None,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request should be rate limited
        
        Args:
            request: FastAPI request
            action: Action identifier (login, register, etc.)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed, raises HTTPException if limited
        """
        if not self.enabled or not self.redis_client:
            return True
        
        max_requests = max_requests or settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        key = self._get_key(request, action)
        
        try:
            # Use Redis pipeline for atomic operations
            async with self.redis_client.pipeline() as pipe:
                # Get current count
                current_count = await self.redis_client.get(key)
                
                if current_count is None:
                    # First request, set key with expiry
                    await pipe.setex(key, window_seconds, 1)
                    await pipe.execute()
                    return True
                
                current_count = int(current_count)
                
                if current_count >= max_requests:
                    # Rate limit exceeded
                    ttl = await self.redis_client.ttl(key)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {ttl} seconds.",
                        headers={"Retry-After": str(ttl)}
                    )
                
                # Increment counter
                await self.redis_client.incr(key)
                return True
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fail open - allow request if rate limiting fails
            return True
    
    async def add_failed_attempt(
        self,
        identifier: str,
        action: str = "login",
        max_attempts: int = 5,
        lockout_seconds: int = 900  # 15 minutes
    ) -> None:
        """
        Track failed attempts for an identifier (email, username, etc.)
        
        Args:
            identifier: Unique identifier to track
            action: Type of action (login, otp_verify, etc.)
            max_attempts: Maximum attempts before lockout
            lockout_seconds: Lockout duration in seconds
        """
        if not self.enabled or not self.redis_client:
            return
        
        key = f"failed_attempts:{action}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        lockout_key = f"{key}:locked"
        
        try:
            # Check if already locked out
            is_locked = await self.redis_client.get(lockout_key)
            if is_locked:
                ttl = await self.redis_client.ttl(lockout_key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Account temporarily locked. Try again in {ttl} seconds.",
                    headers={"Retry-After": str(ttl)}
                )
            
            # Increment failed attempts
            attempts = await self.redis_client.incr(key)
            
            # Set expiry on first attempt
            if attempts == 1:
                await self.redis_client.expire(key, lockout_seconds)
            
            # Check if should lock out
            if attempts >= max_attempts:
                await self.redis_client.setex(lockout_key, lockout_seconds, "1")
                await self.redis_client.delete(key)
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed attempts. Account locked for {lockout_seconds // 60} minutes.",
                    headers={"Retry-After": str(lockout_seconds)}
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to track failed attempt: {e}")
    
    async def clear_failed_attempts(
        self,
        identifier: str,
        action: str = "login"
    ) -> None:
        """Clear failed attempts for an identifier after successful action"""
        if not self.enabled or not self.redis_client:
            return
        
        key = f"failed_attempts:{action}:{hashlib.sha256(identifier.encode()).hexdigest()}"
        lockout_key = f"{key}:locked"
        
        try:
            await self.redis_client.delete(key, lockout_key)
        except Exception as e:
            logger.error(f"Failed to clear failed attempts: {e}")


# Global instance
rate_limiter = RateLimiter()