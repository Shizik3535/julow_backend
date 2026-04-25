"""Интеграционные тесты GetArchivedProjectsHandler (реальные repos)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_archived_projects import (
    GetArchivedProjectsQuery,
    GetArchivedProjectsHandler,
)


@pytest.mark.integration
class TestGetArchivedProjectsHandler:
    """Тесты GetArchivedProjectsHandler."""

    @pytest.fixture
    def handler(self, project_repo) -> GetArchivedProjectsHandler:
        return GetArchivedProjectsHandler(project_repo=project_repo)

    async def test_get_archived_projects_found(self, handler, project_repo, make_project) -> None:
        ws_id = Id.generate()
        project = await make_project(workspace_id=ws_id)
        project.archive()
        project.clear_domain_events()
        await project_repo.update(project)

        query = GetArchivedProjectsQuery(workspace_id=str(ws_id))
        result = await handler.handle(query)
        assert len(result.items) >= 1

    async def test_get_archived_projects_empty(self, handler, make_project) -> None:
        ws_id = Id.generate()
        await make_project(workspace_id=ws_id)  # active, not archived
        query = GetArchivedProjectsQuery(workspace_id=str(ws_id))
        result = await handler.handle(query)
        assert len(result.items) == 0
