"""Интеграционные тесты GetUserByIdHandler (реальная PostgreSQL)."""

import pytest

from app.context.identity.application.queries.get_user_by_id import GetUserByIdHandler, GetUserByIdQuery
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository
from app.shared.domain.value_objects.id_vo import Id


@pytest.mark.integration
class TestGetUserByIdHandler:
    """Тесты получения пользователя по ID."""

    @pytest.fixture
    def handler(self, user_repo: SqlUserRepository) -> GetUserByIdHandler:
        return GetUserByIdHandler(user_repo=user_repo)

    async def test_get_user_found(self, handler: GetUserByIdHandler, make_user) -> None:
        user = await make_user(email="found@test.com")
        query = GetUserByIdQuery(user_id=str(user.id))
        dto = await handler.handle(query)
        assert dto.id == str(user.id)
        assert dto.email == "found@test.com"

    async def test_get_user_not_found(self, handler: GetUserByIdHandler) -> None:
        query = GetUserByIdQuery(user_id=str(Id.generate()))
        with pytest.raises(UserNotFoundException):
            await handler.handle(query)
