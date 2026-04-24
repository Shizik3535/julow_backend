"""Интеграционные тесты OnUserRegisteredCreateProfile (реальная PostgreSQL)."""

import pytest

from app.context.profile.application.event_handlers.on_user_registered_create_profile import (
    OnUserRegisteredCreateProfile,
)
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestOnUserRegisteredCreateProfile:
    """Тесты создания профиля из события UserRegistered."""

    @pytest.fixture
    def handler(self, profile_repo: SqlUserProfileRepository) -> OnUserRegisteredCreateProfile:
        return OnUserRegisteredCreateProfile(profile_repo=profile_repo)

    async def test_creates_profile(
        self, handler: OnUserRegisteredCreateProfile, profile_repo: SqlUserProfileRepository
    ) -> None:
        user_id = Id.generate()
        event = {
            "event_type": "UserRegistered",
            "payload": {"user_id": str(user_id)},
        }
        await handler.handle(event)

        profile = await profile_repo.get_by_user_id(user_id)
        assert profile is not None
        assert profile.user_id == user_id

    async def test_idempotent_skips_if_exists(
        self, handler: OnUserRegisteredCreateProfile, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        existing = await make_profile()
        event = {
            "event_type": "UserRegistered",
            "payload": {"user_id": str(existing.user_id)},
        }
        # Повторный вызов не должен бросить исключение
        await handler.handle(event)

        # Профиль должен остаться тем же
        found = await profile_repo.get_by_user_id(existing.user_id)
        assert found is not None
        assert found.id == existing.id

    async def test_ignores_non_user_registered_event(
        self, handler: OnUserRegisteredCreateProfile, profile_repo: SqlUserProfileRepository
    ) -> None:
        user_id = Id.generate()
        event = {
            "event_type": "UserLoggedIn",
            "payload": {"user_id": str(user_id)},
        }
        await handler.handle(event)

        profile = await profile_repo.get_by_user_id(user_id)
        assert profile is None

    async def test_ignores_event_without_user_id(
        self, handler: OnUserRegisteredCreateProfile, profile_repo: SqlUserProfileRepository
    ) -> None:
        event = {
            "event_type": "UserRegistered",
            "payload": {},
        }
        # Не должно бросить исключение
        await handler.handle(event)
