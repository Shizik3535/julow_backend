"""Интеграционные тесты GetRolesHandler (реальная PostgreSQL)."""

import pytest

from app.context.identity.application.queries.get_roles import GetRolesHandler, GetRolesQuery
from app.context.identity.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository


@pytest.mark.integration
class TestGetRolesHandler:
    """Тесты получения списка ролей."""

    @pytest.fixture
    def handler(self, role_repo: SqlRoleRepository) -> GetRolesHandler:
        return GetRolesHandler(role_repo=role_repo)

    async def test_get_all_roles(self, handler: GetRolesHandler, make_role) -> None:
        await make_role(name="role-q1")
        await make_role(name="role-q2")
        query = GetRolesQuery()
        result = await handler.handle(query)
        assert result.total >= 2

    async def test_get_system_only(self, handler: GetRolesHandler, make_role) -> None:
        await make_role(name="sys-q", is_system=True)
        await make_role(name="custom-q", is_system=False)
        query = GetRolesQuery(system_only=True)
        result = await handler.handle(query)
        assert all(r.is_system for r in result.items)

    async def test_get_roles_with_pagination(self, handler: GetRolesHandler, make_role) -> None:
        for i in range(5):
            await make_role()
        query = GetRolesQuery(offset=0, limit=3)
        result = await handler.handle(query)
        assert len(result.items) <= 3
