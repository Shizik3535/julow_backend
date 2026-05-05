"""Интеграционные тесты SqlProjectRepository.get_overdue_by_workspace (реальная PostgreSQL)."""

from datetime import date, timedelta

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.infrastructure.persistence.repositories.sql_project_repository import SqlProjectRepository


@pytest.mark.integration
class TestSqlProjectRepositoryGetOverdueByWorkspace:
    """Тесты получения просроченных проектов по workspace."""

    async def test_returns_overdue_projects_in_workspace(self, project_repo: SqlProjectRepository, make_project) -> None:
        ws_id = Id.generate()
        project = await make_project(workspace_id=ws_id)
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_overdue_by_workspace(ws_id)
        assert any(p.id == project.id for p in results)

    async def test_excludes_projects_from_other_workspace(self, project_repo: SqlProjectRepository, make_project) -> None:
        ws_id = Id.generate()
        other_ws_id = Id.generate()
        project = await make_project(workspace_id=other_ws_id)
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_overdue_by_workspace(ws_id)
        assert not any(p.id == project.id for p in results)

    async def test_excludes_archived_projects_in_workspace(self, project_repo: SqlProjectRepository, make_project) -> None:
        ws_id = Id.generate()
        project = await make_project(workspace_id=ws_id)
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.archive()
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_overdue_by_workspace(ws_id)
        assert not any(p.id == project.id for p in results)

    async def test_excludes_projects_with_future_deadline(self, project_repo: SqlProjectRepository, make_project) -> None:
        ws_id = Id.generate()
        project = await make_project(workspace_id=ws_id)
        project.update_info(deadline=date.today() + timedelta(days=7))
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_overdue_by_workspace(ws_id)
        assert not any(p.id == project.id for p in results)

    async def test_empty_for_workspace_without_overdue(self, project_repo: SqlProjectRepository, make_project) -> None:
        ws_id = Id.generate()
        project = await make_project(workspace_id=ws_id)
        # deadline is None by default

        results = await project_repo.get_overdue_by_workspace(ws_id)
        assert not any(p.id == project.id for p in results)
