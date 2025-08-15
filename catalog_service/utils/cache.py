# catalog_service/utils/cache.py

import json
import hashlib
from functools import wraps
import redis

try:
    redis_client = redis.Redis(
        host="redis", port=6379, db=0,
        decode_responses=True, socket_connect_timeout=5, socket_timeout=5,
        retry_on_timeout=True
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False

def _gen_key(prefix: str, fname: str, args, kwargs) -> str:
    raw = str(args) + str(sorted(kwargs.items()))
    return f"{prefix}:{fname}:{hashlib.md5(raw.encode()).hexdigest()}"

def cache_result(ttl: int = 300, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not REDIS_AVAILABLE:
                return await func(*args, **kwargs)
            key = _gen_key(key_prefix, func.__name__, args, kwargs)
            try:
                cached = redis_client.get(key)
                if cached is not None:
                    return json.loads(cached)
            except Exception:
                pass
            result = await func(*args, **kwargs)
            try:
                redis_client.setex(key, ttl, json.dumps(result, default=str))
            except Exception:
                pass
            return result
        return wrapper
    return decorator
