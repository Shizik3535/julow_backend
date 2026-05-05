"""Интеграционные тесты SqlProjectRepository.get_overdue_projects (реальная PostgreSQL)."""

from datetime import date, timedelta

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.value_objects.project_status import ProjectStatus
from app.context.project.infrastructure.persistence.repositories.sql_project_repository import SqlProjectRepository


@pytest.mark.integration
class TestSqlProjectRepositoryGetOverdueProjects:
    """Тесты получения просроченных проектов."""

    async def test_returns_projects_with_past_deadline(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project()
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_overdue_projects()
        assert any(p.id == project.id for p in results)

    async def test_excludes_projects_with_future_deadline(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project()
        project.update_info(deadline=date.today() + timedelta(days=7))
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_overdue_projects()
        assert not any(p.id == project.id for p in results)

    async def test_excludes_archived_projects(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project()
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.archive()
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_overdue_projects()
        assert not any(p.id == project.id for p in results)

    async def test_excludes_suspended_projects(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project()
        project.update_info(deadline=date.today() - timedelta(days=1))
        project.suspend(reason="test")
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_overdue_projects()
        assert not any(p.id == project.id for p in results)

    async def test_excludes_projects_without_deadline(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project()
        # deadline is None by default

        results = await project_repo.get_overdue_projects()
        assert not any(p.id == project.id for p in results)

    async def test_includes_projects_with_today_deadline_not_overdue(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project()
        project.update_info(deadline=date.today())
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_overdue_projects()
        assert not any(p.id == project.id for p in results)
