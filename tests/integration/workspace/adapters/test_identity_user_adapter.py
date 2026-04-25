"""
Интеграционные тесты IdentityUserAdapter (inboard).

Адаптер делегирует в IdentityUserProvider (outboard Identity BC).
Тестируем через stub provider, проверяя корректность маппинга DTO → dict.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.application.ports.integration.outboard.identity_user_provider import IdentityUserProvider
from app.context.workspace.infrastructure.integration.inboard.identity_user_adapter import IdentityUserAdapter


class _StubIdentityUserProvider(IdentityUserProvider):
    """Stub outboard-провайдер Identity BC."""

    def __init__(self, users: dict[str, UserDTO] | None = None):
        self._users = users or {}

    async def get_user(self, user_id: str) -> UserDTO | None:
        return self._users.get(user_id)

    async def get_users(self, user_ids: list[str]) -> list[UserDTO]:
        return [self._users[uid] for uid in user_ids if uid in self._users]


def _make_user_dto(user_id: str, email: str = "user@test.com", status: str = "active") -> UserDTO:
    from datetime import datetime, timezone
    return UserDTO(
        id=user_id,
        email=email,
        status=status,
        role_ids=[],
        is_email_confirmed=True,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )


@pytest.mark.integration
class TestIdentityUserAdapter:
    """Тесты IdentityUserAdapter."""

    async def test_user_exists_true(self) -> None:
        uid = str(Id.generate())
        provider = _StubIdentityUserProvider({uid: _make_user_dto(uid)})
        adapter = IdentityUserAdapter(identity_user_provider=provider)

        result = await adapter.user_exists(uid)
        assert result is True

    async def test_user_exists_false(self) -> None:
        provider = _StubIdentityUserProvider({})
        adapter = IdentityUserAdapter(identity_user_provider=provider)

        result = await adapter.user_exists("nonexistent-id")
        assert result is False

    async def test_get_user_found(self) -> None:
        uid = str(Id.generate())
        dto = _make_user_dto(uid, email="found@test.com")
        provider = _StubIdentityUserProvider({uid: dto})
        adapter = IdentityUserAdapter(identity_user_provider=provider)

        result = await adapter.get_user(uid)
        assert result is not None
        assert result["id"] == uid
        assert result["email"] == "found@test.com"
        assert result["status"] == "active"

    async def test_get_user_not_found(self) -> None:
        provider = _StubIdentityUserProvider({})
        adapter = IdentityUserAdapter(identity_user_provider=provider)

        result = await adapter.get_user("nonexistent-id")
        assert result is None
