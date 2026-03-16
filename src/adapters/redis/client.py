from redis.asyncio import Redis

from src.core.settings import settings

# Module-level singleton — one connection pool shared across the process.
# Async Redis client from redis-py (>= 4.2) with native asyncio support.
_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.redis.url,
            decode_responses=True,
        )
    return _redis_client


async def close_redis_client() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
