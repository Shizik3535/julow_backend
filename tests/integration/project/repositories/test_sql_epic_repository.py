"""Интеграционные тесты SqlEpicRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.epic import Epic
from app.context.project.domain.value_objects.epic_status import EpicStatus
from app.context.project.infrastructure.persistence.repositories.sql_epic_repository import SqlEpicRepository


@pytest.mark.integration
class TestSqlEpicRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, epic_repo: SqlEpicRepository, make_epic) -> None:
        epic = await make_epic()
        found = await epic_repo.get_by_id(epic.id)
        assert found is not None
        assert found.id == epic.id

    async def test_add_persists_attributes(self, epic_repo: SqlEpicRepository, make_epic) -> None:
        epic = await make_epic(name="Epic Feature")
        found = await epic_repo.get_by_id(epic.id)
        assert found is not None
        assert found.name == "Epic Feature"
        assert found.status == EpicStatus.OPEN


@pytest.mark.integration
class TestSqlEpicRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_project(self, epic_repo: SqlEpicRepository, make_epic) -> None:
        epic = await make_epic()
        results = await epic_repo.get_by_project(epic.project_id)
        assert len(results) >= 1

    async def test_get_by_project_empty(self, epic_repo: SqlEpicRepository, make_project) -> None:
        proj = await make_project()
        results = await epic_repo.get_by_project(proj.id)
        assert results == []

    async def test_get_by_status(self, epic_repo: SqlEpicRepository, make_epic) -> None:
        epic = await make_epic()
        results = await epic_repo.get_by_status(epic.project_id, EpicStatus.OPEN.value)
        assert len(results) >= 1

    async def test_get_by_owner(self, epic_repo: SqlEpicRepository, make_epic, make_user) -> None:
        user = await make_user()
        epic = await make_epic(owner_id=user.id)
        results = await epic_repo.get_by_owner(user.id)
        assert len(results) >= 1


@pytest.mark.integration
class TestSqlEpicRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_name(self, epic_repo: SqlEpicRepository, make_epic) -> None:
        epic = await make_epic(name="Old Epic")
        epic.update(name="New Epic")
        epic.clear_domain_events()
        await epic_repo.update(epic)

        found = await epic_repo.get_by_id(epic.id)
        assert found is not None
        assert found.name == "New Epic"

    async def test_update_status(self, epic_repo: SqlEpicRepository, make_epic) -> None:
        epic = await make_epic()
        epic.change_status(EpicStatus.IN_PROGRESS)
        epic.clear_domain_events()
        await epic_repo.update(epic)

        found = await epic_repo.get_by_id(epic.id)
        assert found is not None
        assert found.status == EpicStatus.IN_PROGRESS


@pytest.mark.integration
class TestSqlEpicRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, epic_repo: SqlEpicRepository, make_epic) -> None:
        epic = await make_epic()
        await epic_repo.delete(epic.id)
        found = await epic_repo.get_by_id(epic.id)
        assert found is None

    async def test_get_by_id_not_found(self, epic_repo: SqlEpicRepository) -> None:
        found = await epic_repo.get_by_id(Id.generate())
        assert found is None
