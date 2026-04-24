"""
Profile BC conftest — фикстуры для integration-тестов Profile.

Предоставляет mapper, repository, seed-хелперы.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.aggregates.user_profile import UserProfile
from app.context.profile.infrastructure.persistence.mappers.user_profile_mapper import UserProfileMapper
from app.context.profile.infrastructure.persistence.orm_models.user_profile_orm import UserProfileORM
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)


# ── Mapper ───────────────────────────────────────────────────────────────────


@pytest.fixture
def profile_mapper() -> UserProfileMapper:
    return UserProfileMapper()


# ── Repository ───────────────────────────────────────────────────────────────


@pytest.fixture
def profile_repo(db_session: AsyncSession, profile_mapper: UserProfileMapper) -> SqlUserProfileRepository:
    return SqlUserProfileRepository(session=db_session, mapper=profile_mapper)


# ── Seed Helpers ─────────────────────────────────────────────────────────────


@pytest.fixture
def make_profile(profile_repo: SqlUserProfileRepository):
    """Фабрика: создаёт UserProfile и сохраняет в БД."""

    async def _make(user_id: Id | None = None) -> UserProfile:
        uid = user_id or Id.generate()
        profile = UserProfile.create(user_id=uid)
        profile.clear_domain_events()
        await profile_repo.add(profile)
        return profile

    return _make
