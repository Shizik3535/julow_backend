"""Интеграционные тесты SqlSessionRepository (реальная PostgreSQL)."""

import uuid

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.refresh_token import RefreshToken
from app.context.identity.domain.value_objects.session_status import SessionStatus
from app.context.identity.infrastructure.persistence.repositories.sql_session_repository import SqlSessionRepository


@pytest.mark.integration
class TestSqlSessionRepositoryBasic:
    """Базовые CRUD тесты сессий."""

    async def test_add_and_get_by_id(self, session_repo: SqlSessionRepository, make_session) -> None:
        session = await make_session()
        found = await session_repo.get_by_id(session.id)
        assert found is not None
        assert found.id == session.id
        assert found.status == SessionStatus.ACTIVE

    async def test_get_by_id_not_found(self, session_repo: SqlSessionRepository) -> None:
        found = await session_repo.get_by_id(Id.generate())
        assert found is None


@pytest.mark.integration
class TestSqlSessionRepositoryQueries:
    """Тесты поиска сессий."""

    async def test_get_active_by_user(self, session_repo: SqlSessionRepository, make_session) -> None:
        user_id = Id.generate()
        s1 = await make_session(user_id=user_id)
        s2 = await make_session(user_id=user_id)
        # Создаём сессию другого пользователя
        await make_session(user_id=Id.generate())

        active = await session_repo.get_active_by_user(user_id)
        assert len(active) == 2
        assert all(s.user_id == user_id for s in active)

    async def test_get_by_user(self, session_repo: SqlSessionRepository, make_session) -> None:
        user_id = Id.generate()
        await make_session(user_id=user_id)
        await make_session(user_id=user_id)

        sessions = await session_repo.get_by_user(user_id)
        assert len(sessions) >= 2

    async def test_count_active_by_user(self, session_repo: SqlSessionRepository, make_session) -> None:
        user_id = Id.generate()
        await make_session(user_id=user_id)
        await make_session(user_id=user_id)

        count = await session_repo.count_active_by_user(user_id)
        assert count == 2

    async def test_get_by_refresh_token(self, session_repo: SqlSessionRepository, _ensure_user) -> None:
        user_id = Id.generate()
        await _ensure_user(user_id)
        token = RefreshToken(value=f"test-refresh-{uuid.uuid4().hex}")
        session = Session.create(
            user_id=user_id,
            device_info=DeviceInfo(user_agent="TokenTest"),
            ip_address=IpAddress("10.0.0.2"),
            refresh_token=token,
        )
        session.clear_domain_events()
        await session_repo.add(session)

        found = await session_repo.get_by_refresh_token(token)
        assert found is not None
        assert found.id == session.id


@pytest.mark.integration
class TestSqlSessionRepositoryTerminate:
    """Тесты завершения сессий."""

    async def test_terminate_by_user(self, session_repo: SqlSessionRepository, make_session) -> None:
        user_id = Id.generate()
        s = await make_session(user_id=user_id)
        await session_repo.terminate_by_user(user_id, s.id)

        found = await session_repo.get_by_id(s.id)
        assert found is not None
        assert found.status == SessionStatus.TERMINATED

    async def test_terminate_all_by_user(self, session_repo: SqlSessionRepository, make_session) -> None:
        user_id = Id.generate()
        s1 = await make_session(user_id=user_id)
        s2 = await make_session(user_id=user_id)
        s3 = await make_session(user_id=user_id)

        # Завершаем все кроме s1
        await session_repo.terminate_all_by_user(user_id, except_session_id=s1.id)

        found_s1 = await session_repo.get_by_id(s1.id)
        found_s2 = await session_repo.get_by_id(s2.id)
        found_s3 = await session_repo.get_by_id(s3.id)

        assert found_s1 is not None and found_s1.status == SessionStatus.ACTIVE
        assert found_s2 is not None and found_s2.status == SessionStatus.TERMINATED
        assert found_s3 is not None and found_s3.status == SessionStatus.TERMINATED

    async def test_terminate_all_by_user_no_except(self, session_repo: SqlSessionRepository, make_session) -> None:
        user_id = Id.generate()
        s1 = await make_session(user_id=user_id)
        s2 = await make_session(user_id=user_id)

        await session_repo.terminate_all_by_user(user_id)

        found_s1 = await session_repo.get_by_id(s1.id)
        found_s2 = await session_repo.get_by_id(s2.id)

        assert found_s1 is not None and found_s1.status == SessionStatus.TERMINATED
        assert found_s2 is not None and found_s2.status == SessionStatus.TERMINATED
