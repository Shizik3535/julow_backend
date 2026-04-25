"""Интеграционные тесты SearchTasksHandler (реальные repos + стабы портов)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.application.queries.search_tasks import SearchTasksQuery, SearchTasksHandler
from app.context.task.application.exceptions.authorization_exceptions import InsufficientTaskPermissionsException


@pytest.mark.integration
class TestSearchTasksHandler:
    """Тесты поиска задач — full stack."""

    @pytest.fixture
    def handler(self, task_repo, permission_checker_stub) -> SearchTasksHandler:
        return SearchTasksHandler(task_repo=task_repo, permission_checker=permission_checker_stub)

    async def test_search_by_title(self, handler, make_task) -> None:
        task = await make_task(title="SearchTarget123")
        result = await handler.handle(SearchTasksQuery(caller_id=str(task.reporter_id), filters={"title": "SearchTarget123"}))
        assert result.total >= 1

    async def test_search_empty(self, handler) -> None:
        result = await handler.handle(SearchTasksQuery(caller_id=str(Id.generate()), filters={"title": "Nonexistent"}))
        assert result.total == 0

    async def test_search_with_pagination(self, handler, make_task) -> None:
        for i in range(5):
            await make_task(title=f"PageSearch-{i}")
        result = await handler.handle(SearchTasksQuery(caller_id=str(Id.generate()), offset=0, limit=2))
        assert len(result.items) <= 2

    async def test_search_with_project_permission_denied(self, task_repo, permission_denied_stub, make_task) -> None:
        await make_task(title="DeniedSearch")
        handler = SearchTasksHandler(task_repo=task_repo, permission_checker=permission_denied_stub)
        with pytest.raises(InsufficientTaskPermissionsException):
            await handler.handle(SearchTasksQuery(caller_id=str(Id.generate()), project_id=str(Id.generate()), filters={"title": "DeniedSearch"}))
