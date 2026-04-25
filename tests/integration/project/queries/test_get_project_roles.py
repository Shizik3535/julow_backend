"""Интеграционные тесты GetProjectRolesHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_project_roles import (
    GetProjectRolesQuery,
    GetProjectRolesHandler,
)


@pytest.mark.integration
class TestGetProjectRolesHandler:
    """Тесты GetProjectRolesHandler."""

    @pytest.fixture
    def handler(self, role_repo) -> GetProjectRolesHandler:
        return GetProjectRolesHandler(role_repo=role_repo)

    async def test_get_roles_with_roles(self, handler, make_project_with_membership) -> None:
        data = await make_project_with_membership()
        query = GetProjectRolesQuery(project_id=str(data["project"].id))
        result = await handler.handle(query)
        assert len(result.items) >= 1

    async def test_get_roles_empty(self, handler, make_project) -> None:
        project = await make_project()
        query = GetProjectRolesQuery(project_id=str(project.id))
        result = await handler.handle(query)
        assert len(result.items) == 0
