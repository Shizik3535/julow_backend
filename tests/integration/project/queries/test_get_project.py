"""Интеграционные тесты GetProjectHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_project import (
    GetProjectQuery,
    GetProjectHandler,
)
from app.context.project.domain.exceptions.project_exceptions import ProjectNotFoundException


@pytest.mark.integration
class TestGetProjectHandler:
    """Тесты GetProjectHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub) -> GetProjectHandler:
        return GetProjectHandler(project_repo=project_repo, permission_checker=permission_checker_stub)

    async def test_get_project_found(self, handler, make_project) -> None:
        project = await make_project(name="Test Project")
        query = GetProjectQuery(caller_id=str(Id.generate()), project_id=str(project.id))
        result = await handler.handle(query)
        assert result.id == str(project.id)
        assert result.name == "Test Project"

    async def test_get_project_not_found(self, handler) -> None:
        query = GetProjectQuery(caller_id=str(Id.generate()), project_id=str(Id.generate()))
        with pytest.raises(ProjectNotFoundException):
            await handler.handle(query)
