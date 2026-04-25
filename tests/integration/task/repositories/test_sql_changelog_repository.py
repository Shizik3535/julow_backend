"""Интеграционные тесты SqlChangelogRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.infrastructure.persistence.repositories.sql_changelog_repository import (
    SqlChangelogRepository,
)


@pytest.mark.integration
class TestSqlChangelogRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_task_id(
        self, changelog_repo: SqlChangelogRepository, make_changelog_entry
    ) -> None:
        entry = await make_changelog_entry(field_name="status_id", old_value="old", new_value="new")
        found = await changelog_repo.get_by_task_id(entry.task_id)
        assert len(found) >= 1
        assert found[0].field_name == "status_id"
        assert found[0].old_value == "old"
        assert found[0].new_value == "new"


@pytest.mark.integration
class TestSqlChangelogRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_task_id_with_pagination(
        self, changelog_repo: SqlChangelogRepository, make_changelog_entry
    ) -> None:
        task_id = Id.generate()
        for i in range(5):
            await make_changelog_entry(task_id=task_id, field_name=f"field_{i}")
        results = await changelog_repo.get_by_task_id(task_id, offset=0, limit=2)
        assert len(results) <= 2

    async def test_get_by_task_and_field(
        self, changelog_repo: SqlChangelogRepository, make_changelog_entry
    ) -> None:
        task_id = Id.generate()
        await make_changelog_entry(task_id=task_id, field_name="priority", old_value="low", new_value="high")
        await make_changelog_entry(task_id=task_id, field_name="status_id", old_value="todo", new_value="done")

        results = await changelog_repo.get_by_task_and_field(task_id, "priority")
        assert len(results) >= 1
        assert all(r.field_name == "priority" for r in results)

    async def test_get_recent_changes(
        self, changelog_repo: SqlChangelogRepository, make_changelog_entry
    ) -> None:
        task_id = Id.generate()
        for i in range(5):
            await make_changelog_entry(task_id=task_id, field_name=f"field_{i}")
        results = await changelog_repo.get_recent_changes(task_id, limit=3)
        assert len(results) <= 3

    async def test_count_by_task(
        self, changelog_repo: SqlChangelogRepository, make_changelog_entry
    ) -> None:
        task_id = Id.generate()
        await make_changelog_entry(task_id=task_id, field_name="field_1")
        await make_changelog_entry(task_id=task_id, field_name="field_2")
        count = await changelog_repo.count_by_task(task_id)
        assert count >= 2

    async def test_get_by_task_id_empty(
        self, changelog_repo: SqlChangelogRepository
    ) -> None:
        results = await changelog_repo.get_by_task_id(Id.generate())
        assert results == []
