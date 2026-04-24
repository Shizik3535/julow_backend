"""Интеграционные тесты OnUserLoggedInCreateSession (реальная PostgreSQL)."""

import pytest

from app.context.identity.application.event_handlers.on_user_logged_in_create_session import (
    OnUserLoggedInCreateSession,
)
from app.context.identity.domain.events.auth_events import UserLoggedIn
from app.context.identity.domain.value_objects.session_status import SessionStatus
from app.context.identity.infrastructure.persistence.repositories.sql_session_repository import SqlSessionRepository
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestOnUserLoggedInCreateSession:
    """Тесты создания сессии из события UserLoggedIn."""

    @pytest.fixture
    def handler(self, session_repo: SqlSessionRepository) -> OnUserLoggedInCreateSession:
        return OnUserLoggedInCreateSession(session_repo=session_repo)

    async def test_creates_session(
        self, handler: OnUserLoggedInCreateSession, session_repo: SqlSessionRepository,
        _ensure_user,
    ) -> None:
        user_id_vo = Id.generate()
        await _ensure_user(user_id_vo)
        user_id = str(user_id_vo)
        event = UserLoggedIn(
            user_id=user_id,
            session_id=str(Id.generate()),
            ip="192.168.1.1",
            device="Chrome/Linux",
            aggregate_id=Id.generate(),
            aggregate_type="UserAuth",
        )
        await handler.handle(event)

        sessions = await session_repo.get_active_by_user(Id.from_string(user_id))
        assert len(sessions) >= 1
        session = sessions[0]
        assert str(session.user_id) == user_id
        assert session.status == SessionStatus.ACTIVE
        assert session.device_info.user_agent == "Chrome/Linux"
