"""Интеграционные тесты GetActiveSprintHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_active_sprint import (
    GetActiveSprintQuery,
    GetActiveSprintHandler,
)
from app.context.project.domain.exceptions.sprint_exceptions import SprintNotFoundException


@pytest.mark.integration
class TestGetActiveSprintHandler:
    """Тесты GetActiveSprintHandler."""

    @pytest.fixture
    def handler(self, sprint_repo) -> GetActiveSprintHandler:
        return GetActiveSprintHandler(sprint_repo=sprint_repo)

    async def test_get_active_sprint_found(self, handler, sprint_repo, make_sprint) -> None:
        sprint = await make_sprint()
        sprint.start()
        sprint.clear_domain_events()
        await sprint_repo.update(sprint)

        query = GetActiveSprintQuery(project_id=str(sprint.project_id))
        result = await handler.handle(query)
        assert result is not None
        assert result.status == "active"

    async def test_get_active_sprint_not_found(self, handler, make_sprint) -> None:
        sprint = await make_sprint()  # PLANNING, not active
        query = GetActiveSprintQuery(project_id=str(sprint.project_id))
        with pytest.raises(SprintNotFoundException):
            await handler.handle(query)
