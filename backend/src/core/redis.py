"""
VoiceFlow AI — Redis Connection Manager
Provides async Redis client for caching, pub/sub, and session management.
"""

from typing import Optional

import redis.asyncio as aioredis

from src.core.config import settings

_redis_pool: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or create a Redis connection from the pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return _redis_pool


async def close_redis() -> None:
    """Close the Redis connection pool."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.close()
        _redis_pool = None


class RedisCache:
    """Simple async Redis cache wrapper."""

    def __init__(self, prefix: str = "vf"):
        self.prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[str]:
        r = await get_redis()
        return await r.get(self._key(key))

    async def set(self, key: str, value: str, expire: int = 3600) -> None:
        r = await get_redis()
        await r.set(self._key(key), value, ex=expire)

    async def delete(self, key: str) -> None:
        r = await get_redis()
        await r.delete(self._key(key))

    async def exists(self, key: str) -> bool:
        r = await get_redis()
        return bool(await r.exists(self._key(key)))

    async def increment(self, key: str, expire: int = 60) -> int:
        r = await get_redis()
        pipe = r.pipeline()
        pipe.incr(self._key(key))
        pipe.expire(self._key(key), expire)
        results = await pipe.execute()
        return results[0]


cache = RedisCache()
