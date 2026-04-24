from redis.asyncio import Redis

from app.core.config.redis_settings import RedisSettings
from app.shared.application.ports.cache.cache_port import CachePort
from app.shared.infrastructure.cache.redis_cache_adapter import RedisCacheAdapter


def create_redis_client(settings: RedisSettings) -> Redis:
    """Создать async Redis клиент."""
    return Redis.from_url(settings.url, decode_responses=True)


def create_cache_adapter(redis_client: Redis, key_prefix: str = "", default_ttl: int | None = None) -> CachePort:
    """Создать RedisCacheAdapter."""
    return RedisCacheAdapter(
        redis_client=redis_client,
        key_prefix=key_prefix,
        default_ttl=default_ttl,
    )
