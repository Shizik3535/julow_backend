"""Интеграционные тесты SearchProjectsHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.search_projects import (
    SearchProjectsQuery,
    SearchProjectsHandler,
)


@pytest.mark.integration
class TestSearchProjectsHandler:
    """Тесты SearchProjectsHandler."""

    @pytest.fixture
    def handler(self, project_repo, permission_checker_stub) -> SearchProjectsHandler:
        return SearchProjectsHandler(project_repo=project_repo, permission_checker=permission_checker_stub)

    async def test_search_with_results(self, handler, make_project) -> None:
        await make_project(name="AlphaProject")
        query = SearchProjectsQuery(caller_id=str(Id.generate()), offset=0, limit=100, filters={"query": "Alpha"})
        result = await handler.handle(query)
        assert result.total >= 1

    async def test_search_empty(self, handler) -> None:
        query = SearchProjectsQuery(caller_id=str(Id.generate()), offset=0, limit=100, filters={"query": "nonexistent"})
        result = await handler.handle(query)
        assert result.total == 0

    async def test_search_pagination(self, handler, make_project) -> None:
        await make_project(name="Page1")
        await make_project(name="Page2")
        query = SearchProjectsQuery(caller_id=str(Id.generate()), offset=0, limit=1)
        result = await handler.handle(query)
        assert len(result.items) <= 1
