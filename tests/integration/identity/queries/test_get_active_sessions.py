"""Интеграционные тесты GetActiveSessionsHandler (реальная PostgreSQL)."""

import pytest

from app.context.identity.application.queries.get_active_sessions import (
    GetActiveSessionsHandler,
    GetActiveSessionsQuery,
)
from app.context.identity.infrastructure.persistence.repositories.sql_session_repository import SqlSessionRepository
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestGetActiveSessionsHandler:
    """Тесты получения активных сессий."""

    @pytest.fixture
    def handler(self, session_repo: SqlSessionRepository) -> GetActiveSessionsHandler:
        return GetActiveSessionsHandler(session_repo=session_repo)

    async def test_get_active_sessions(self, handler: GetActiveSessionsHandler, make_session) -> None:
        user_id = Id.generate()
        await make_session(user_id=user_id)
        await make_session(user_id=user_id)

        query = GetActiveSessionsQuery(user_id=str(user_id))
        result = await handler.handle(query)
        assert result.total == 2
        assert len(result.items) == 2

    async def test_get_active_sessions_empty(self, handler: GetActiveSessionsHandler) -> None:
        query = GetActiveSessionsQuery(user_id=str(Id.generate()))
        result = await handler.handle(query)
        assert result.total == 0
        assert result.items == []
