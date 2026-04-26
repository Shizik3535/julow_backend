"""Интеграционные тесты SqlProjectRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project import Project
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.project_status import ProjectStatus
from app.context.project.infrastructure.persistence.repositories.sql_project_repository import SqlProjectRepository


@pytest.mark.integration
class TestSqlProjectRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project()
        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.id == project.id

    async def test_add_persists_attributes(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project(name="Test Project", methodology=Methodology.SCRUM)
        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.name == "Test Project"
        assert found.methodology == Methodology.SCRUM
        assert found.status == ProjectStatus.ACTIVE

    async def test_add_persists_owner_ids(self, project_repo: SqlProjectRepository, make_project, make_user) -> None:
        user = await make_user()
        project = await make_project(owner_id=user.id)
        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert user.id in found.owner_ids


@pytest.mark.integration
class TestSqlProjectRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_workspace(self, project_repo: SqlProjectRepository, make_project) -> None:
        ws_id = Id.generate()
        await make_project(workspace_id=ws_id)
        await make_project(workspace_id=ws_id)
        await make_project()  # другой workspace

        results = await project_repo.get_by_workspace(ws_id)
        assert len(results) == 2

    async def test_get_by_workspace_empty(self, project_repo: SqlProjectRepository) -> None:
        results = await project_repo.get_by_workspace(Id.generate())
        assert results == []

    async def test_get_by_methodology(self, project_repo: SqlProjectRepository, make_project) -> None:
        await make_project(methodology=Methodology.SCRUM)
        await make_project(methodology=Methodology.KANBAN)

        results = await project_repo.get_by_methodology(Methodology.SCRUM.value)
        assert len(results) >= 1
        assert all(p.methodology == Methodology.SCRUM for p in results)

    async def test_get_archived_by_workspace(self, project_repo: SqlProjectRepository, make_project) -> None:
        ws_id = Id.generate()
        project = await make_project(workspace_id=ws_id)
        project.archive()
        project.clear_domain_events()
        await project_repo.update(project)

        results = await project_repo.get_archived_by_workspace(ws_id)
        assert len(results) == 1
        assert results[0].status == ProjectStatus.ARCHIVED

    async def test_search_by_name(self, project_repo: SqlProjectRepository, make_project) -> None:
        await make_project(name="UniqueAlphaProject")
        await make_project(name="OtherProject")

        results = await project_repo.search(filters={"query": "Alpha"})
        assert len(results) >= 1
        assert any("Alpha" in p.name for p in results)


@pytest.mark.integration
class TestSqlProjectRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_name(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project(name="Old Name")
        project.update_info(name="New Name")
        project.clear_domain_events()
        await project_repo.update(project)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.name == "New Name"

    async def test_update_status(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project()
        project.archive()
        project.clear_domain_events()
        await project_repo.update(project)

        found = await project_repo.get_by_id(project.id)
        assert found is not None
        assert found.status == ProjectStatus.ARCHIVED


@pytest.mark.integration
class TestSqlProjectRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, project_repo: SqlProjectRepository, make_project) -> None:
        project = await make_project()
        await project_repo.delete(project.id)
        found = await project_repo.get_by_id(project.id)
        assert found is None

    async def test_get_by_id_not_found(self, project_repo: SqlProjectRepository) -> None:
        found = await project_repo.get_by_id(Id.generate())
        assert found is None
