"""Интеграционные тесты GetProjectRoleHandler (реальные repos)."""

import pytest

from app.context.project.domain.exceptions.project_role_exceptions import ProjectRoleNotFoundException
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_project_role import (
    GetProjectRoleQuery,
    GetProjectRoleHandler,
)


@pytest.mark.integration
class TestGetProjectRoleHandler:
    """Тесты GetProjectRoleHandler."""

    @pytest.fixture
    def handler(self, role_repo, permission_checker_stub) -> GetProjectRoleHandler:
        return GetProjectRoleHandler(role_repo=role_repo, permission_checker=permission_checker_stub)

    async def test_get_role_found(self, handler, make_project_role) -> None:
        role = await make_project_role(name="TestRole")
        query = GetProjectRoleQuery(caller_id=str(Id.generate()), role_id=str(role.id))
        result = await handler.handle(query)
        assert result.name == "TestRole"

    async def test_get_role_not_found(self, handler) -> None:
        query = GetProjectRoleQuery(caller_id=str(Id.generate()), role_id=str(Id.generate()))
        with pytest.raises(ProjectRoleNotFoundException):
            await handler.handle(query)
