"""Интеграционные тесты GetProjectsByMethodologyHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_projects_by_methodology import (
    GetProjectsByMethodologyQuery,
    GetProjectsByMethodologyHandler,
)
from app.context.project.domain.value_objects.methodology import Methodology


@pytest.mark.integration
class TestGetProjectsByMethodologyHandler:
    """Тесты GetProjectsByMethodologyHandler."""

    @pytest.fixture
    def handler(self, project_repo) -> GetProjectsByMethodologyHandler:
        return GetProjectsByMethodologyHandler(project_repo=project_repo)

    async def test_get_projects_by_methodology_found(self, handler, make_project) -> None:
        await make_project(methodology=Methodology.SCRUM)
        query = GetProjectsByMethodologyQuery(methodology="scrum")
        result = await handler.handle(query)
        assert len(result.items) >= 1

    async def test_get_projects_by_methodology_empty(self, handler) -> None:
        query = GetProjectsByMethodologyQuery(methodology="waterfall")
        result = await handler.handle(query)
        assert len(result.items) == 0
