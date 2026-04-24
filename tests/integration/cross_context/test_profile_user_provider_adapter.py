"""Интеграционные тесты ProfileUserProviderAdapter (реальная PostgreSQL)."""

import pytest

from app.context.profile.application.dto.profile_dto import ProfileDTO
from app.context.profile.infrastructure.integration.outboard.profile_user_provider_adapter import (
    ProfileUserProviderAdapter,
)
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestProfileUserProviderAdapter:
    """Тесты ProfileUserProviderAdapter: get_profile, get_profiles."""

    @pytest.fixture
    def adapter(self, profile_repo: SqlUserProfileRepository) -> ProfileUserProviderAdapter:
        return ProfileUserProviderAdapter(profile_repo=profile_repo)

    # -- get_profile --

    async def test_get_profile_returns_dto(
        self, adapter: ProfileUserProviderAdapter, make_profile,
    ) -> None:
        uid = Id.generate()
        profile = await make_profile(user_id=uid)

        dto = await adapter.get_profile(str(uid))
        assert dto is not None
        assert isinstance(dto, ProfileDTO)
        assert dto.user_id == str(uid)
        assert dto.id == str(profile.id)

    async def test_get_profile_returns_none_for_unknown(
        self, adapter: ProfileUserProviderAdapter,
    ) -> None:
        result = await adapter.get_profile(str(Id.generate()))
        assert result is None

    async def test_get_profile_default_fields(
        self, adapter: ProfileUserProviderAdapter, make_profile,
    ) -> None:
        uid = Id.generate()
        await make_profile(user_id=uid)

        dto = await adapter.get_profile(str(uid))
        assert dto is not None
        assert dto.avatar_url is None
        assert dto.bio is None
        assert dto.job_title is None

    # -- get_profiles --

    async def test_get_profiles_returns_list(
        self, adapter: ProfileUserProviderAdapter, make_profile,
    ) -> None:
        uid1 = Id.generate()
        uid2 = Id.generate()
        await make_profile(user_id=uid1)
        await make_profile(user_id=uid2)

        dtos = await adapter.get_profiles([str(uid1), str(uid2)])
        assert len(dtos) == 2
        returned_ids = {d.user_id for d in dtos}
        assert str(uid1) in returned_ids
        assert str(uid2) in returned_ids

    async def test_get_profiles_skips_unknown(
        self, adapter: ProfileUserProviderAdapter, make_profile,
    ) -> None:
        uid = Id.generate()
        await make_profile(user_id=uid)

        dtos = await adapter.get_profiles([str(uid), str(Id.generate())])
        assert len(dtos) == 1
        assert dtos[0].user_id == str(uid)

    async def test_get_profiles_empty_list(
        self, adapter: ProfileUserProviderAdapter,
    ) -> None:
        dtos = await adapter.get_profiles([])
        assert dtos == []
