"""Интеграционные тесты GetSprintHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_sprint import (
    GetSprintQuery,
    GetSprintHandler,
)


@pytest.mark.integration
class TestGetSprintHandler:
    """Тесты GetSprintHandler."""

    @pytest.fixture
    def handler(self, sprint_repo) -> GetSprintHandler:
        return GetSprintHandler(sprint_repo=sprint_repo)

    async def test_get_sprint_found(self, handler, make_sprint) -> None:
        sprint = await make_sprint(name="Sprint 1")
        query = GetSprintQuery(sprint_id=str(sprint.id))
        result = await handler.handle(query)
        assert result.name == "Sprint 1"

    async def test_get_sprint_not_found(self, handler) -> None:
        query = GetSprintQuery(sprint_id=str(Id.generate()))
        from app.context.project.domain.exceptions.sprint_exceptions import SprintNotFoundException
        with pytest.raises(SprintNotFoundException):
            await handler.handle(query)
