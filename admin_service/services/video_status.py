# admin_service/services/video_status.py

# admin_service/services/video_status.py
import json
from typing import Dict, Optional

import redis.asyncio as redis
from core.config import settings

REDIS_STATUS_PREFIX = "video_status:"
DEFAULT_TTL = 60 * 60 * 24  # 24h

_redis_client: Optional[redis.Redis] = None  # type: ignore


async def get_redis() -> "redis.Redis":  # type: ignore
    """Создать или вернуть singleton-подключение к Redis."""
    global _redis_client
    if not settings.REDIS_URL:
        raise RuntimeError("REDIS_URL is not set")
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def set_video_status(video_id: str, data: dict, ttl: int = DEFAULT_TTL) -> None:
    r = await get_redis()
    key = f"{REDIS_STATUS_PREFIX}{video_id}"
    await r.set(key, json.dumps(data), ex=ttl)


async def get_video_status(video_id: str) -> Optional[Dict]:
    r = await get_redis()
    key = f"{REDIS_STATUS_PREFIX}{video_id}"
    data = await r.get(key)
    return json.loads(data) if data else None


async def update_video_status(video_id: str, update_dict: dict) -> None:
    cur = await get_video_status(video_id)
    merged = {**(cur or {}), **update_dict}
    await set_video_status(video_id, merged)


async def delete_video_status(video_id: str) -> bool:
    r = await get_redis()
    key = f"{REDIS_STATUS_PREFIX}{video_id}"
    deleted = await r.delete(key)
    return deleted > 0


async def get_all_statuses() -> Dict[str, Dict]:
    r = await get_redis()
    keys = await r.keys(f"{REDIS_STATUS_PREFIX}*")
    out: Dict[str, Dict] = {}
    for key in keys:
        vid = key.replace(REDIS_STATUS_PREFIX, "")
        data = await r.get(key)
        if data:
            out[vid] = json.loads(data)
    return out


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
