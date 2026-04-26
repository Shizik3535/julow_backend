"""Интеграционные тесты GetProjectsByWorkspaceHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_projects_by_workspace import (
    GetProjectsByWorkspaceQuery,
    GetProjectsByWorkspaceHandler,
)


@pytest.mark.integration
class TestGetProjectsByWorkspaceHandler:
    """Тесты GetProjectsByWorkspaceHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub) -> GetProjectsByWorkspaceHandler:
        return GetProjectsByWorkspaceHandler(project_repo=project_repo, permission_checker=permission_checker_stub)

    async def test_get_projects_by_workspace_found(self, handler, make_project) -> None:
        ws_id = Id.generate()
        await make_project(workspace_id=ws_id)
        query = GetProjectsByWorkspaceQuery(caller_id=str(Id.generate()), workspace_id=str(ws_id))
        result = await handler.handle(query)
        assert len(result.items) >= 1

    async def test_get_projects_by_workspace_empty(self, handler) -> None:
        query = GetProjectsByWorkspaceQuery(caller_id=str(Id.generate()), workspace_id=str(Id.generate()))
        result = await handler.handle(query)
        assert len(result.items) == 0
