"""Интеграционные тесты GetProfileHandler (реальная PostgreSQL)."""

import pytest

from app.context.profile.application.queries.get_profile import GetProfileHandler, GetProfileQuery
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestGetProfileHandler:
    """Тесты получения профиля по user_id."""

    @pytest.fixture
    def handler(self, profile_repo: SqlUserProfileRepository) -> GetProfileHandler:
        return GetProfileHandler(profile_repo=profile_repo)

    async def test_get_profile_found(self, handler: GetProfileHandler, make_profile) -> None:
        profile = await make_profile()
        query = GetProfileQuery(user_id=str(profile.user_id))
        dto = await handler.handle(query)
        assert dto.id == str(profile.id)
        assert dto.user_id == str(profile.user_id)

    async def test_get_profile_with_personal_info(
        self, handler: GetProfileHandler, make_profile, profile_repo: SqlUserProfileRepository
    ) -> None:
        profile = await make_profile()
        profile.update_personal_info(bio="Test bio", job_title="Tester")
        profile.clear_domain_events()
        await profile_repo.update(profile)

        query = GetProfileQuery(user_id=str(profile.user_id))
        dto = await handler.handle(query)
        assert dto.bio == "Test bio"
        assert dto.job_title == "Tester"

    async def test_get_profile_not_found(self, handler: GetProfileHandler) -> None:
        query = GetProfileQuery(user_id=str(Id.generate()))
        with pytest.raises(ProfileNotFoundException):
            await handler.handle(query)
