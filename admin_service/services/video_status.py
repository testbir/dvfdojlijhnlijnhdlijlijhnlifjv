import redis.asyncio as redis
import json
from typing import Dict, Optional
from core.config import settings

# Redis key prefix for video statuses
REDIS_STATUS_PREFIX = "video_status:"
# Default TTL - 24 hours
DEFAULT_TTL = 60 * 60 * 24

# Global Redis connection
_redis_client: Optional[redis.Redis] = None  # 🟢 Исправлено

async def get_redis() -> redis.Redis:
    """Get or create Redis connection"""
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.from_url(  # 🟢 `redis.from_url`, не `await`
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    return _redis_client


async def set_video_status(video_id: str, data: dict, ttl: int = DEFAULT_TTL) -> None:
    redis = await get_redis()
    key = f"{REDIS_STATUS_PREFIX}{video_id}"
    await redis.set(key, json.dumps(data), ex=ttl)


async def get_video_status(video_id: str) -> Optional[Dict]:
    redis = await get_redis()
    key = f"{REDIS_STATUS_PREFIX}{video_id}"
    data = await redis.get(key)

    if data:
        return json.loads(data)
    return None


async def update_video_status(video_id: str, update_dict: dict) -> None:
    current_status = await get_video_status(video_id)

    if current_status is None:
        await set_video_status(video_id, update_dict)
    else:
        current_status.update(update_dict)
        await set_video_status(video_id, current_status)


async def delete_video_status(video_id: str) -> bool:  # Добавить возвращаемый тип
    redis = await get_redis()
    key = f"{REDIS_STATUS_PREFIX}{video_id}"
    result = await redis.delete(key)
    return result > 0  # Возвращаем True если ключ был удален


async def get_all_statuses() -> Dict[str, Dict]:
    redis = await get_redis()
    keys = await redis.keys(f"{REDIS_STATUS_PREFIX}*")

    result = {}
    for key in keys:
        video_id = key.replace(REDIS_STATUS_PREFIX, "")
        data = await redis.get(key)
        if data:
            result[video_id] = json.loads(data)

    return result


async def close_redis() -> None:
    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
