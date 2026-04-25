"""Интеграционные тесты SqlTaskRepository (реальная PostgreSQL)."""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.domain.value_objects.task_priority import TaskPriority
from app.context.task.domain.value_objects.task_status import TaskStatus
from app.context.task.domain.value_objects.label import Label
from app.context.task.domain.value_objects.relation_type import RelationType
from app.context.task.domain.value_objects.task_order import TaskOrder
from app.context.task.infrastructure.persistence.repositories.sql_task_repository import SqlTaskRepository


@pytest.mark.integration
class TestSqlTaskRepositoryAdd:
    """Тесты добавления."""

    async def test_add_and_get_by_id(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.id == task.id

    async def test_add_persists_attributes(self, task_repo: SqlTaskRepository, make_task) -> None:
        reporter = Id.generate()
        task = await make_task(
            title="Test Task",
            task_type=TaskType.BUG,
            reporter_id=reporter,
        )
        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.title == "Test Task"
        assert found.task_type == TaskType.BUG
        assert found.reporter_id == reporter
        assert found.status == TaskStatus.ACTIVE
        assert found.priority == TaskPriority.NONE

    async def test_add_with_labels(self, task_repo: SqlTaskRepository, make_task) -> None:
        labels = [Label(name="bug", color=None), Label(name="critical", color=None)]
        task = await make_task()
        for label in labels:
            task.add_label(label)
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.labels) == 2
        label_names = {l.name for l in found.labels}
        assert label_names == {"bug", "critical"}

    async def test_add_with_parent_task(self, task_repo: SqlTaskRepository, make_task) -> None:
        parent = await make_task()
        child = await make_task(title="Child", parent_task_id=parent.id)
        found = await task_repo.get_by_id(child.id)
        assert found is not None
        assert found.parent_task_id == parent.id

    async def test_get_by_id_not_found(self, task_repo: SqlTaskRepository) -> None:
        found = await task_repo.get_by_id(Id.generate())
        assert found is None


@pytest.mark.integration
class TestSqlTaskRepositorySearch:
    """Тесты поиска."""

    async def test_get_by_project_found(self, task_repo: SqlTaskRepository, make_task) -> None:
        project_id = Id.generate()
        task = await make_task(project_id=project_id)
        found = await task_repo.get_by_project(project_id)
        assert len(found) >= 1
        assert any(t.id == task.id for t in found)

    async def test_get_by_project_empty(self, task_repo: SqlTaskRepository) -> None:
        found = await task_repo.get_by_project(Id.generate())
        assert found == []

    async def test_get_by_reporter_found(self, task_repo: SqlTaskRepository, make_task) -> None:
        reporter_id = Id.generate()
        task = await make_task(reporter_id=reporter_id)
        found = await task_repo.get_by_reporter(reporter_id)
        assert len(found) >= 1
        assert any(t.id == task.id for t in found)

    async def test_get_by_reporter_empty(self, task_repo: SqlTaskRepository) -> None:
        found = await task_repo.get_by_reporter(Id.generate())
        assert found == []

    async def test_get_subtasks_found(self, task_repo: SqlTaskRepository, make_task) -> None:
        parent = await make_task()
        child = await make_task(title="Subtask", parent_task_id=parent.id)
        found = await task_repo.get_subtasks(parent.id)
        assert len(found) >= 1
        assert any(t.id == child.id for t in found)

    async def test_get_subtasks_empty(self, task_repo: SqlTaskRepository, make_task) -> None:
        parent = await make_task()
        found = await task_repo.get_subtasks(parent.id)
        assert found == []

    async def test_get_by_sprint_found(self, task_repo: SqlTaskRepository, make_task) -> None:
        sprint_id = Id.generate()
        task = await make_task()
        task.assign_to_sprint(sprint_id)
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_sprint(sprint_id)
        assert len(found) >= 1
        assert any(t.id == task.id for t in found)

    async def test_get_by_sprint_empty(self, task_repo: SqlTaskRepository) -> None:
        found = await task_repo.get_by_sprint(Id.generate())
        assert found == []

    async def test_get_by_epic_found(self, task_repo: SqlTaskRepository, make_task) -> None:
        epic_id = Id.generate()
        task = await make_task(epic_id=epic_id)
        found = await task_repo.get_by_epic(epic_id)
        assert len(found) >= 1
        assert any(t.id == task.id for t in found)

    async def test_get_by_epic_empty(self, task_repo: SqlTaskRepository) -> None:
        found = await task_repo.get_by_epic(Id.generate())
        assert found == []

    async def test_get_by_status_found(self, task_repo: SqlTaskRepository, make_task) -> None:
        project_id = Id.generate()
        status_id = Id.generate()
        task = await make_task(project_id=project_id)
        task.change_status(status_id)
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_status(project_id=project_id, status_id=status_id)
        assert len(found) >= 1

    async def test_get_by_status_empty(self, task_repo: SqlTaskRepository) -> None:
        found = await task_repo.get_by_status(
            project_id=Id.generate(), status_id=Id.generate()
        )
        assert found == []

    async def test_get_by_labels_found(self, task_repo: SqlTaskRepository, make_task) -> None:
        project_id = Id.generate()
        task = await make_task(project_id=project_id)
        task.add_label(Label(name="frontend", color=None))
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_labels(project_id=project_id, label_names=["frontend"])
        assert len(found) >= 1

    async def test_get_by_labels_empty(self, task_repo: SqlTaskRepository) -> None:
        found = await task_repo.get_by_labels(
            project_id=Id.generate(), label_names=["nonexistent"]
        )
        assert found == []

    async def test_search_by_title(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task(title="UniqueSearchTitle123")
        results = await task_repo.search(filters={"title": "UniqueSearchTitle123"})
        assert any(t.id == task.id for t in results)

    async def test_search_pagination(self, task_repo: SqlTaskRepository, make_task) -> None:
        for i in range(5):
            await make_task(title=f"PageTask-{i}")
        results = await task_repo.search(offset=0, limit=2)
        assert len(results) <= 2

    async def test_count_by_project(self, task_repo: SqlTaskRepository, make_task) -> None:
        project_id = Id.generate()
        await make_task(project_id=project_id, title="Count1")
        await make_task(project_id=project_id, title="Count2")
        count = await task_repo.count_by_project(project_id)
        assert count >= 2

    async def test_count_by_status(self, task_repo: SqlTaskRepository, make_task) -> None:
        project_id = Id.generate()
        status_id = Id.generate()
        task = await make_task(project_id=project_id)
        task.change_status(status_id)
        task.clear_domain_events()
        await task_repo.update(task)

        count = await task_repo.count_by_status(project_id=project_id, status_id=status_id)
        assert count >= 1


@pytest.mark.integration
class TestSqlTaskRepositoryUpdate:
    """Тесты обновления."""

    async def test_update_scalar_fields(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        task.update_info(title="Updated Title")
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.title == "Updated Title"

    async def test_update_priority(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        task.change_priority(TaskPriority.HIGH)
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.priority == TaskPriority.HIGH

    async def test_update_with_checklists(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        cl = task.add_checklist("My Checklist")
        task.add_checklist_item(cl.id, "Item 1")
        task.add_checklist_item(cl.id, "Item 2")
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.checklists) == 1
        assert found.checklists[0].title == "My Checklist"
        assert len(found.checklists[0].items) == 2

    async def test_update_with_relations(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        related_id = Id.generate()
        created_by = Id.generate()
        task.add_relation(related_id, RelationType.BLOCKS, created_by)
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.relations) == 1
        assert found.relations[0].related_task_id == related_id
        assert found.relations[0].relation_type == RelationType.BLOCKS

    async def test_update_with_watchers(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        watcher_id = Id.generate()
        task.add_watcher(watcher_id)
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.watchers) == 1
        assert found.watchers[0].user_id == watcher_id

    async def test_update_with_attachments(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        file_id = Id.generate()
        uploaded_by = Id.generate()
        task.add_attachment(file_id=file_id, filename="doc.pdf", size_bytes=1024, uploaded_by=uploaded_by)
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.attachments) == 1
        assert found.attachments[0].filename == "doc.pdf"
        assert found.attachments[0].size_bytes == 1024

    async def test_update_labels_sync(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        task.add_label(Label(name="label1", color=None))
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert len(found.labels) == 1

        found.remove_label("label1")
        found.add_label(Label(name="label2", color=None))
        found.clear_domain_events()
        await task_repo.update(found)

        updated = await task_repo.get_by_id(task.id)
        assert updated is not None
        label_names = {l.name for l in updated.labels}
        assert label_names == {"label2"}

    async def test_update_clears_children(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        cl = task.add_checklist("To Remove")
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert len(found.checklists) == 1

        found.remove_checklist(cl.id)
        found.clear_domain_events()
        await task_repo.update(found)

        updated = await task_repo.get_by_id(task.id)
        assert updated is not None
        assert len(updated.checklists) == 0

    async def test_update_status_to_archived(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        task.archive()
        task.clear_domain_events()
        await task_repo.update(task)

        found = await task_repo.get_by_id(task.id)
        assert found is not None
        assert found.status == TaskStatus.ARCHIVED


@pytest.mark.integration
class TestSqlTaskRepositoryDelete:
    """Тесты удаления."""

    async def test_delete(self, task_repo: SqlTaskRepository, make_task) -> None:
        task = await make_task()
        await task_repo.delete(task.id)
        found = await task_repo.get_by_id(task.id)
        assert found is None
