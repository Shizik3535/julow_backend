"""Unit-тесты GetOverdueProjectsHandler."""

from datetime import date, timedelta
from unittest.mock import AsyncMock

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.application.queries.get_overdue_projects import (
    GetOverdueProjectsQuery,
    GetOverdueProjectsHandler,
)
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.value_objects.methodology import Methodology


@pytest.mark.unit
class TestGetOverdueProjectsHandler:
    """Тесты GetOverdueProjectsHandler."""

    @pytest.fixture
    def project_repo(self) -> AsyncMock:
        repo = AsyncMock()
        repo.get_overdue_projects.return_value = []
        repo.get_overdue_by_workspace.return_value = []
        repo.get_by_member.return_value = []
        return repo

    @pytest.fixture
    def permission_checker(self) -> AsyncMock:
        checker = AsyncMock()
        checker.has_permission.return_value = True
        return checker

    @pytest.fixture
    def handler(self, project_repo, permission_checker) -> GetOverdueProjectsHandler:
        return GetOverdueProjectsHandler(project_repo=project_repo, permission_checker=permission_checker)

    def _make_overdue_project(self, owner_id: Id | None = None, workspace_id: Id | None = None) -> Project:
        owner = owner_id or Id.generate()
        ws = workspace_id or Id.generate()
        project = Project.create(
            name="Overdue Project",
            workspace_id=ws,
            owner_id=owner,
            methodology=Methodology.KANBAN,
        )
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.clear_domain_events()
        return project

    async def test_my_overdue_returns_member_projects(self, handler, project_repo) -> None:
        owner_id = Id.generate()
        project = self._make_overdue_project(owner_id=owner_id)
        project_repo.get_overdue_projects.return_value = [project]
        project_repo.get_by_member.return_value = [project]

        query = GetOverdueProjectsQuery(caller_id=str(owner_id))
        result = await handler.handle(query)

        assert len(result.items) == 1
        assert result.items[0].id == str(project.id)

    async def test_my_overdue_returns_project_where_user_is_member(self, handler, project_repo) -> None:
        caller_id = Id.generate()
        other_owner = Id.generate()
        project = self._make_overdue_project(owner_id=other_owner)
        project_repo.get_overdue_projects.return_value = [project]
        project_repo.get_by_member.return_value = [project]

        query = GetOverdueProjectsQuery(caller_id=str(caller_id))
        result = await handler.handle(query)

        assert len(result.items) == 1

    async def test_my_overdue_excludes_non_member_projects(self, handler, project_repo) -> None:
        caller_id = Id.generate()
        other_owner = Id.generate()
        project = self._make_overdue_project(owner_id=other_owner)
        project_repo.get_overdue_projects.return_value = [project]
        project_repo.get_by_member.return_value = []

        query = GetOverdueProjectsQuery(caller_id=str(caller_id))
        result = await handler.handle(query)

        assert len(result.items) == 0

    async def test_workspace_overdue_returns_filtered_projects(self, handler, project_repo) -> None:
        ws_id = Id.generate()
        project = self._make_overdue_project(workspace_id=ws_id)
        project_repo.get_overdue_by_workspace.return_value = [project]

        query = GetOverdueProjectsQuery(caller_id=str(Id.generate()), workspace_id=str(ws_id))
        result = await handler.handle(query)

        assert len(result.items) == 1
        project_repo.get_overdue_by_workspace.assert_called_once()

    async def test_workspace_overdue_checks_permission(self, handler, project_repo, permission_checker) -> None:
        ws_id = Id.generate()
        project = self._make_overdue_project(workspace_id=ws_id)
        project_repo.get_overdue_by_workspace.return_value = [project]
        permission_checker.has_permission.return_value = False

        query = GetOverdueProjectsQuery(caller_id=str(Id.generate()), workspace_id=str(ws_id))
        result = await handler.handle(query)

        assert len(result.items) == 0

    async def test_no_overdue_returns_empty(self, handler, project_repo) -> None:
        query = GetOverdueProjectsQuery(caller_id=str(Id.generate()))
        result = await handler.handle(query)

        assert len(result.items) == 0
        assert result.total == 0
