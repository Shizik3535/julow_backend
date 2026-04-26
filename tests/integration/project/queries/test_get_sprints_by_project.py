"""Интеграционные тесты GetSprintsByProjectHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_sprints_by_project import (
    GetSprintsByProjectQuery,
    GetSprintsByProjectHandler,
)


@pytest.mark.integration
class TestGetSprintsByProjectHandler:
    """Тесты GetSprintsByProjectHandler."""

    @pytest.fixture
    def handler(self, sprint_repo, permission_checker_stub) -> GetSprintsByProjectHandler:
        return GetSprintsByProjectHandler(sprint_repo=sprint_repo, permission_checker=permission_checker_stub)

    async def test_get_sprints_with_sprints(self, handler, make_sprint) -> None:
        sprint = await make_sprint()
        query = GetSprintsByProjectQuery(caller_id=str(Id.generate()), project_id=str(sprint.project_id))
        result = await handler.handle(query)
        assert len(result.items) >= 1

    async def test_get_sprints_empty(self, handler, make_project) -> None:
        project = await make_project()
        query = GetSprintsByProjectQuery(caller_id=str(Id.generate()), project_id=str(project.id))
        result = await handler.handle(query)
        assert len(result.items) == 0
