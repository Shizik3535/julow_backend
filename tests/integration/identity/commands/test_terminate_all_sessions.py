"""Интеграционные тесты TerminateAllSessionsHandler (реальная PostgreSQL)."""

import pytest

from app.context.identity.application.commands.terminate_all_sessions import (
    TerminateAllSessionsCommand,
    TerminateAllSessionsHandler,
)
from app.context.identity.domain.value_objects.session_status import SessionStatus
from app.context.identity.infrastructure.persistence.repositories.sql_session_repository import SqlSessionRepository
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestTerminateAllSessionsHandler:
    """Тесты завершения всех сессий кроме текущей — full stack."""

    @pytest.fixture
    def handler(self, session_repo: SqlSessionRepository) -> TerminateAllSessionsHandler:
        return TerminateAllSessionsHandler(session_repo=session_repo)

    async def test_terminate_all_except_current(
        self, handler: TerminateAllSessionsHandler, make_session, session_repo: SqlSessionRepository
    ) -> None:
        user_id = Id.generate()
        current = await make_session(user_id=user_id)
        other1 = await make_session(user_id=user_id)
        other2 = await make_session(user_id=user_id)

        cmd = TerminateAllSessionsCommand(
            user_id=str(user_id),
            current_session_id=str(current.id),
        )
        result = await handler.handle(cmd)
        assert result == 2

        # Текущая сессия осталась активной
        found_current = await session_repo.get_by_id(current.id)
        assert found_current is not None
        assert found_current.status == SessionStatus.ACTIVE

        # Остальные завершены
        found_other1 = await session_repo.get_by_id(other1.id)
        found_other2 = await session_repo.get_by_id(other2.id)
        assert found_other1 is not None and found_other1.status == SessionStatus.TERMINATED
        assert found_other2 is not None and found_other2.status == SessionStatus.TERMINATED

    async def test_terminate_all_no_other_sessions(
        self, handler: TerminateAllSessionsHandler, make_session
    ) -> None:
        user_id = Id.generate()
        current = await make_session(user_id=user_id)

        cmd = TerminateAllSessionsCommand(
            user_id=str(user_id),
            current_session_id=str(current.id),
        )
        result = await handler.handle(cmd)
        assert result == 0
