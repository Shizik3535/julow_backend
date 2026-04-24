from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import get_logger
from app.shared.application.ports.cache.cache_port import CachePort

logger = get_logger(__name__)


class RedisCacheAdapter(CachePort):
    """
    Реализация CachePort на основе Redis (async).

    Сериализует значения в JSON для хранения.
    Поддерживает TTL, glob-паттерны для очистки,
    префиксы ключей для изоляции Bounded Context'ов.

    Аргументы конструктора:
        redis_client: Async Redis клиент.
        key_prefix: Префикс для ключей (для изоляции контекстов).
        default_ttl: TTL по умолчанию в секундах.
    """

    def __init__(
        self,
        redis_client: Redis,
        key_prefix: str = "",
        default_ttl: int | None = None,
    ) -> None:
        self._redis = redis_client
        self._prefix = key_prefix
        self._default_ttl = default_ttl or settings.redis.default_ttl

    def _make_key(self, key: str) -> str:
        return f"{self._prefix}:{key}" if self._prefix else key

    async def get(self, key: str) -> Any | None:
        raw = await self._redis.get(self._make_key(key))
        if raw is None:
            logger.debug("Cache miss", key=key)
            return None
        logger.debug("Cache hit", key=key)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        serialized = json.dumps(value, default=str, ensure_ascii=False)
        effective_ttl = ttl if ttl is not None else self._default_ttl
        await self._redis.set(self._make_key(key), serialized, ex=effective_ttl)
        logger.debug("Cache set", key=key, ttl=effective_ttl)

    async def delete(self, key: str) -> None:
        await self._redis.delete(self._make_key(key))
        logger.debug("Cache deleted", key=key)

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.exists(self._make_key(key)))

    async def clear(self, pattern: str = "*") -> int:
        full_pattern = self._make_key(pattern)
        keys = []
        async for key in self._redis.scan_iter(match=full_pattern):
            keys.append(key)
        if not keys:
            return 0
        deleted = await self._redis.delete(*keys)
        logger.info("Cache cleared", pattern=full_pattern, deleted=deleted)
        return deleted
