"""
Cross-context conftest — фикстуры из Identity и Profile BC.

Cross-context тесты требуют доступа к репозиториям и seed-хелперам
обоих BC. Фикстуры дублируют те, что определены в identity/ и profile/
conftest-ах, чтобы не нарушать иерархию pytest conftest.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id

# ── Identity ────────────────────────────────────────────────────────────────

from app.context.identity.domain.aggregates.role import Role
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.value_objects.auth_provider import AuthProvider

from app.context.identity.infrastructure.persistence.mappers.role_mapper import RoleMapper
from app.context.identity.infrastructure.persistence.mappers.user_mapper import UserMapper
from app.context.identity.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository

# ── Profile ─────────────────────────────────────────────────────────────────

from app.context.profile.domain.aggregates.user_profile import UserProfile
from app.context.profile.infrastructure.persistence.mappers.user_profile_mapper import UserProfileMapper
from app.context.profile.infrastructure.persistence.repositories.sql_user_profile_repository import (
    SqlUserProfileRepository,
)


# ── Identity Mappers & Repos ────────────────────────────────────────────────


@pytest.fixture
def user_mapper() -> UserMapper:
    return UserMapper()


@pytest.fixture
def role_mapper() -> RoleMapper:
    return RoleMapper()


@pytest.fixture
def user_repo(db_session: AsyncSession, user_mapper: UserMapper) -> SqlUserRepository:
    return SqlUserRepository(session=db_session, mapper=user_mapper)


@pytest.fixture
def role_repo(db_session: AsyncSession, role_mapper: RoleMapper) -> SqlRoleRepository:
    return SqlRoleRepository(session=db_session, mapper=role_mapper)


# ── Profile Mapper & Repo ───────────────────────────────────────────────────


@pytest.fixture
def profile_mapper() -> UserProfileMapper:
    return UserProfileMapper()


@pytest.fixture
def profile_repo(db_session: AsyncSession, profile_mapper: UserProfileMapper) -> SqlUserProfileRepository:
    return SqlUserProfileRepository(session=db_session, mapper=profile_mapper)


# ── Identity Seed Helpers ───────────────────────────────────────────────────


@pytest.fixture
def _ensure_user(user_repo: SqlUserRepository):
    """Хелпер: гарантирует наличие User в БД для FK-зависимостей."""
    _created: set[Id] = set()

    async def _fn(user_id: Id | None = None) -> User:
        uid = user_id or Id.generate()
        found = await user_repo.get_by_id(uid)
        if found is not None:
            _created.add(uid)
            return found
        email_vo = Email(f"auto-{uuid.uuid4().hex[:8]}@test.com")
        user = User(id=uid, email=email_vo)
        user.clear_domain_events()
        await user_repo.add(user)
        _created.add(uid)
        return user

    return _fn


@pytest.fixture
def make_user(user_repo: SqlUserRepository, _ensure_user):
    """Фабрика: создаёт User и сохраняет в БД."""

    async def _make(
        email: str | None = None,
        auth_provider: AuthProvider = AuthProvider.EMAIL_PASSWORD,
    ) -> User:
        email_vo = Email(email or f"user-{uuid.uuid4().hex[:8]}@test.com")
        user = User.register(email=email_vo, auth_provider=auth_provider)
        user.clear_domain_events()
        await user_repo.add(user)
        return user

    return _make


@pytest.fixture
def make_role(role_repo: SqlRoleRepository):
    """Фабрика: создаёт Role и сохраняет в БД. Возвращает существующую роль по имени, если есть."""

    async def _make(
        name: str | None = None,
        permissions: list[str] | None = None,
        is_system: bool = False,
    ) -> Role:
        role_name = name or f"role-{uuid.uuid4().hex[:6]}"
        existing = await role_repo.get_by_name(role_name)
        if existing is not None:
            return existing
        role = Role(
            name=role_name,
            permissions=permissions or [],
            is_system=is_system,
        )
        await role_repo.add(role)
        return role

    return _make


# ── Profile Seed Helpers ────────────────────────────────────────────────────


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
