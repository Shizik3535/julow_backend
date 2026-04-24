"""
Identity BC conftest — фикстуры для integration-тестов Identity.

Предоставляет mappers, repositories, seed-хелперы и реальные порты.
"""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress

from app.context.identity.domain.aggregates.role import Role
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.aggregates.user import User
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.value_objects.auth_provider import AuthProvider
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.password_hash import PasswordHash

from app.context.identity.infrastructure.persistence.mappers.role_mapper import RoleMapper
from app.context.identity.infrastructure.persistence.mappers.session_mapper import SessionMapper
from app.context.identity.infrastructure.persistence.mappers.user_auth_mapper import UserAuthMapper
from app.context.identity.infrastructure.persistence.mappers.user_mapper import UserMapper


from app.context.identity.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository
from app.context.identity.infrastructure.persistence.repositories.sql_session_repository import SqlSessionRepository
from app.context.identity.infrastructure.persistence.repositories.sql_user_auth_repository import (
    SqlUserAuthRepository,
)
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository


# ── Mappers ──────────────────────────────────────────────────────────────────


@pytest.fixture
def user_mapper() -> UserMapper:
    return UserMapper()


@pytest.fixture
def session_mapper() -> SessionMapper:
    return SessionMapper()


@pytest.fixture
def role_mapper() -> RoleMapper:
    return RoleMapper()


@pytest.fixture
def user_auth_mapper() -> UserAuthMapper:
    return UserAuthMapper()


# ── Repositories ─────────────────────────────────────────────────────────────


@pytest.fixture
def user_repo(db_session: AsyncSession, user_mapper: UserMapper) -> SqlUserRepository:
    return SqlUserRepository(session=db_session, mapper=user_mapper)


@pytest.fixture
def session_repo(db_session: AsyncSession, session_mapper: SessionMapper) -> SqlSessionRepository:
    return SqlSessionRepository(session=db_session, mapper=session_mapper)


@pytest.fixture
def role_repo(db_session: AsyncSession, role_mapper: RoleMapper) -> SqlRoleRepository:
    return SqlRoleRepository(session=db_session, mapper=role_mapper)


@pytest.fixture
def user_auth_repo(db_session: AsyncSession, user_auth_mapper: UserAuthMapper) -> SqlUserAuthRepository:
    return SqlUserAuthRepository(session=db_session, mapper=user_auth_mapper)


# ── Seed Helpers ─────────────────────────────────────────────────────────────


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
        user = User(
            id=uid,
            email=email_vo,
        )
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


@pytest.fixture
def make_user_auth(user_auth_repo: SqlUserAuthRepository, _ensure_user):
    """Фабрика: создаёт UserAuth и сохраняет в БД."""

    async def _make(
        user_id: Id | None = None,
        email: str | None = None,
        password_hash: str = "hashed-password",
    ) -> UserAuth:
        uid = user_id or Id.generate()
        await _ensure_user(uid)
        email_vo = Email(email or f"auth-{uuid.uuid4().hex[:8]}@test.com")
        user_auth = UserAuth.create_for_email_auth(
            user_id=uid,
            email=email_vo,
            password_hash=PasswordHash(value=password_hash),
        )
        await user_auth_repo.add(user_auth)
        return user_auth

    return _make


@pytest.fixture
def make_session(session_repo: SqlSessionRepository, _ensure_user):
    """Фабрика: создаёт Session и сохраняет в БД."""

    async def _make(
        user_id: Id | None = None,
    ) -> Session:
        uid = user_id or Id.generate()
        await _ensure_user(uid)
        session = Session.create(
            user_id=uid,
            device_info=DeviceInfo(user_agent="TestBrowser/1.0"),
            ip_address=IpAddress("10.0.0.1"),
        )
        session.clear_domain_events()
        await session_repo.add(session)
        return session

    return _make
