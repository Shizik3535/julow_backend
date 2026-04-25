"""Интеграционные тесты GetEpicsByProjectHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_epics_by_project import (
    GetEpicsByProjectQuery,
    GetEpicsByProjectHandler,
)


@pytest.mark.integration
class TestGetEpicsByProjectHandler:
    """Тесты GetEpicsByProjectHandler."""

    @pytest.fixture
    def handler(self, epic_repo) -> GetEpicsByProjectHandler:
        return GetEpicsByProjectHandler(epic_repo=epic_repo)

    async def test_get_epics_with_epics(self, handler, make_epic) -> None:
        epic = await make_epic()
        query = GetEpicsByProjectQuery(project_id=str(epic.project_id))
        result = await handler.handle(query)
        assert len(result.items) >= 1

    async def test_get_epics_empty(self, handler, make_project) -> None:
        project = await make_project()
        query = GetEpicsByProjectQuery(project_id=str(project.id))
        result = await handler.handle(query)
        assert len(result.items) == 0
