"""Интеграционные тесты GetUserByEmailHandler (реальная PostgreSQL)."""

import pytest

from app.context.identity.application.queries.get_user_by_email import (
    GetUserByEmailHandler,
    GetUserByEmailQuery,
)
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository


@pytest.mark.integration
class TestGetUserByEmailHandler:
    """Тесты получения пользователя по email."""

    @pytest.fixture
    def handler(self, user_repo: SqlUserRepository) -> GetUserByEmailHandler:
        return GetUserByEmailHandler(user_repo=user_repo)

    async def test_get_user_by_email_found(self, handler: GetUserByEmailHandler, make_user) -> None:
        user = await make_user(email="byemail@test.com")
        query = GetUserByEmailQuery(email="byemail@test.com")
        dto = await handler.handle(query)
        assert dto.id == str(user.id)
        assert dto.email == "byemail@test.com"

    async def test_get_user_by_email_not_found(self, handler: GetUserByEmailHandler) -> None:
        query = GetUserByEmailQuery(email="nope@test.com")
        with pytest.raises(UserNotFoundException):
            await handler.handle(query)
