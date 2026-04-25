"""Интеграционные тесты IdentityUserAdapter (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.integration.inboard.identity_user_adapter import (
    IdentityUserAdapter,
)


class _StubIdentityUserProvider:
    """Stub IdentityUserProvider для тестов."""

    def __init__(self, exists: bool = True):
        self._exists = exists

    async def get_user(self, user_id: str):
        if self._exists:
            from unittest.mock import MagicMock
            user = MagicMock()
            user.id = user_id
            user.email = "stub@test.com"
            user.status = "active"
            return user
        return None


@pytest.mark.integration
class TestIdentityUserAdapter:
    """Тесты IdentityUserAdapter — inboard adapter."""

    async def test_user_exists_true(self) -> None:
        provider = _StubIdentityUserProvider(exists=True)
        adapter = IdentityUserAdapter(identity_user_provider=provider)
        result = await adapter.user_exists(str(Id.generate()))
        assert result is True

    async def test_user_exists_false(self) -> None:
        provider = _StubIdentityUserProvider(exists=False)
        adapter = IdentityUserAdapter(identity_user_provider=provider)
        result = await adapter.user_exists(str(Id.generate()))
        assert result is False

    async def test_get_user_found(self) -> None:
        provider = _StubIdentityUserProvider(exists=True)
        adapter = IdentityUserAdapter(identity_user_provider=provider)
        result = await adapter.get_user(str(Id.generate()))
        assert result is not None
        assert "id" in result

    async def test_get_user_not_found(self) -> None:
        provider = _StubIdentityUserProvider(exists=False)
        adapter = IdentityUserAdapter(identity_user_provider=provider)
        result = await adapter.get_user(str(Id.generate()))
        assert result is None
