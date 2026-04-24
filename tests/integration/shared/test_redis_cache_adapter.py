"""Интеграционные тесты RedisCacheAdapter (реальный Redis)."""

import pytest

from app.shared.infrastructure.cache.redis_cache_adapter import RedisCacheAdapter


@pytest.mark.integration
class TestRedisCacheAdapter:
    """Тесты кэширования через реальный Redis."""

    @pytest.fixture
    def adapter(self, clean_redis) -> RedisCacheAdapter:
        return RedisCacheAdapter(
            redis_client=clean_redis,
            key_prefix="test",
            default_ttl=60,
        )

    async def test_set_and_get(self, adapter: RedisCacheAdapter) -> None:
        await adapter.set("key1", {"name": "value"})
        result = await adapter.get("key1")
        assert result == {"name": "value"}

    async def test_get_missing_key_returns_none(self, adapter: RedisCacheAdapter) -> None:
        result = await adapter.get("nonexistent")
        assert result is None

    async def test_delete(self, adapter: RedisCacheAdapter) -> None:
        await adapter.set("to-delete", "data")
        await adapter.delete("to-delete")
        result = await adapter.get("to-delete")
        assert result is None

    async def test_exists(self, adapter: RedisCacheAdapter) -> None:
        await adapter.set("exists-key", 42)
        assert await adapter.exists("exists-key") is True
        assert await adapter.exists("no-key") is False

    async def test_clear_by_pattern(self, adapter: RedisCacheAdapter) -> None:
        await adapter.set("a1", "x")
        await adapter.set("a2", "y")
        await adapter.set("b1", "z")
        deleted = await adapter.clear("a*")
        assert deleted == 2
        assert await adapter.get("a1") is None
        assert await adapter.get("b1") == "z"

    async def test_set_with_custom_ttl(self, adapter: RedisCacheAdapter) -> None:
        await adapter.set("ttl-key", "data", ttl=1)
        result = await adapter.get("ttl-key")
        assert result == "data"

    async def test_prefix_isolation(self, clean_redis) -> None:
        adapter_a = RedisCacheAdapter(redis_client=clean_redis, key_prefix="ctx_a", default_ttl=60)
        adapter_b = RedisCacheAdapter(redis_client=clean_redis, key_prefix="ctx_b", default_ttl=60)

        await adapter_a.set("shared", "from_a")
        await adapter_b.set("shared", "from_b")

        assert await adapter_a.get("shared") == "from_a"
        assert await adapter_b.get("shared") == "from_b"

    async def test_set_complex_value(self, adapter: RedisCacheAdapter) -> None:
        data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
        await adapter.set("complex", data)
        result = await adapter.get("complex")
        assert result == data
