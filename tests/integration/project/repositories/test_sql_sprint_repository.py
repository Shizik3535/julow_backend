"""Интеграционные тесты SqlSprintRepository (реальная PostgreSQL)."""

import pytest

from datetime import date

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.date_range_vo import DateRange
from app.context.project.domain.aggregates.sprint import Sprint
from app.context.project.domain.value_objects.methodology import Methodology
from app.context.project.domain.value_objects.sprint_status import SprintStatus
from app.context.project.domain.value_objects.sprint_goal import SprintGoal
from app.context.project.infrastructure.persistence.repositories.sql_sprint_repository import SqlSprintRepository


@pytest.mark.integration
class TestSqlSprintRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, sprint_repo: SqlSprintRepository, make_sprint) -> None:
        sprint = await make_sprint()
        found = await sprint_repo.get_by_id(sprint.id)
        assert found is not None
        assert found.id == sprint.id

    async def test_add_persists_attributes(self, sprint_repo: SqlSprintRepository, make_sprint) -> None:
        sprint = await make_sprint(name="Sprint 1", goal=SprintGoal(value="Ship feature X"))
        found = await sprint_repo.get_by_id(sprint.id)
        assert found is not None
        assert found.name == "Sprint 1"
        assert found.goal is not None
        assert found.goal.value == "Ship feature X"
        assert found.status == SprintStatus.PLANNING


@pytest.mark.integration
class TestSqlSprintRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_project(self, sprint_repo: SqlSprintRepository, make_sprint) -> None:
        sprint = await make_sprint()
        results = await sprint_repo.get_by_project(sprint.project_id)
        assert len(results) >= 1

    async def test_get_active_by_project(self, sprint_repo: SqlSprintRepository, make_sprint) -> None:
        sprint = await make_sprint()
        sprint.start()
        sprint.clear_domain_events()
        await sprint_repo.update(sprint)

        found = await sprint_repo.get_active_by_project(sprint.project_id)
        assert len(found) >= 1
        assert found[0].status == SprintStatus.ACTIVE

    async def test_get_active_by_project_none(self, sprint_repo: SqlSprintRepository, make_sprint) -> None:
        sprint = await make_sprint()
        found = await sprint_repo.get_active_by_project(sprint.project_id)
        assert found == []

    async def test_get_by_date_range(self, sprint_repo: SqlSprintRepository, make_project) -> None:
        proj = await make_project(methodology=Methodology.SCRUM)
        sprint = Sprint.create(
            name="Dated Sprint",
            project_id=proj.id,
            date_range=DateRange(start=date(2026, 1, 1), end=date(2026, 1, 31)),
        )
        sprint.clear_domain_events()
        await sprint_repo.add(sprint)

        results = await sprint_repo.get_by_date_range(proj.id, date(2026, 1, 1), date(2026, 1, 31))
        assert len(results) >= 1


@pytest.mark.integration
class TestSqlSprintRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_status(self, sprint_repo: SqlSprintRepository, make_sprint) -> None:
        sprint = await make_sprint()
        sprint.start()
        sprint.clear_domain_events()
        await sprint_repo.update(sprint)

        found = await sprint_repo.get_by_id(sprint.id)
        assert found is not None
        assert found.status == SprintStatus.ACTIVE


@pytest.mark.integration
class TestSqlSprintRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, sprint_repo: SqlSprintRepository, make_sprint) -> None:
        sprint = await make_sprint()
        await sprint_repo.delete(sprint.id)
        found = await sprint_repo.get_by_id(sprint.id)
        assert found is None

    async def test_get_by_id_not_found(self, sprint_repo: SqlSprintRepository) -> None:
        found = await sprint_repo.get_by_id(Id.generate())
        assert found is None
