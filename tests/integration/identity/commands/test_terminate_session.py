"""Интеграционные тесты TerminateSessionHandler (реальная PostgreSQL)."""

import pytest

from app.context.identity.application.commands.terminate_session import (
    TerminateSessionCommand,
    TerminateSessionHandler,
)
from app.context.identity.domain.exceptions.session_exceptions import SessionNotFoundException
from app.context.identity.domain.value_objects.session_status import SessionStatus
from app.context.identity.infrastructure.persistence.repositories.sql_session_repository import SqlSessionRepository
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestTerminateSessionHandler:
    """Тесты завершения одной сессии — full stack."""

    @pytest.fixture
    def handler(self, session_repo: SqlSessionRepository) -> TerminateSessionHandler:
        return TerminateSessionHandler(session_repo=session_repo)

    async def test_terminate_session_success(
        self, handler: TerminateSessionHandler, make_session, session_repo: SqlSessionRepository
    ) -> None:
        user_id = Id.generate()
        session = await make_session(user_id=user_id)

        cmd = TerminateSessionCommand(
            user_id=str(user_id),
            session_id=str(session.id),
        )
        await handler.handle(cmd)

        found = await session_repo.get_by_id(session.id)
        assert found is not None
        assert found.status == SessionStatus.TERMINATED

    async def test_terminate_session_not_found(self, handler: TerminateSessionHandler) -> None:
        cmd = TerminateSessionCommand(
            user_id=str(Id.generate()),
            session_id=str(Id.generate()),
        )
        with pytest.raises(SessionNotFoundException):
            await handler.handle(cmd)
