"""Интеграционные тесты ProfileSettingsProviderAdapter (реальная PostgreSQL)."""

import pytest

from app.context.profile.application.dto.profile_settings_dto import ProfileSettingsDTO
from app.context.profile.infrastructure.integration.outboard.profile_settings_provider_adapter import (
    ProfileSettingsProviderAdapter,
)
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestProfileSettingsProviderAdapter:
    """Тесты ProfileSettingsProviderAdapter: get_settings."""

    @pytest.fixture
    def adapter(self, profile_repo: SqlUserProfileRepository) -> ProfileSettingsProviderAdapter:
        return ProfileSettingsProviderAdapter(profile_repo=profile_repo)

    async def test_get_settings_returns_dto(
        self, adapter: ProfileSettingsProviderAdapter, make_profile,
    ) -> None:
        uid = Id.generate()
        await make_profile(user_id=uid)

        dto = await adapter.get_settings(str(uid))
        assert dto is not None
        assert isinstance(dto, ProfileSettingsDTO)
        assert dto.user_id == str(uid)

    async def test_get_settings_returns_none_for_unknown(
        self, adapter: ProfileSettingsProviderAdapter,
    ) -> None:
        result = await adapter.get_settings(str(Id.generate()))
        assert result is None

    async def test_get_settings_default_localization(
        self, adapter: ProfileSettingsProviderAdapter, make_profile,
    ) -> None:
        uid = Id.generate()
        await make_profile(user_id=uid)

        dto = await adapter.get_settings(str(uid))
        assert dto is not None
        assert dto.language == "en"
        assert dto.timezone == "UTC"
        assert dto.date_format == "YYYY-MM-DD"
        assert dto.time_format == "h24"
        assert dto.week_start_day == "monday"

    async def test_get_settings_default_privacy(
        self, adapter: ProfileSettingsProviderAdapter, make_profile,
    ) -> None:
        uid = Id.generate()
        await make_profile(user_id=uid)

        dto = await adapter.get_settings(str(uid))
        assert dto is not None
        assert dto.profile_visibility == "organization_only"
        assert dto.online_status_visibility == "everyone"
        assert dto.activity_tracking_consent == "granted"
