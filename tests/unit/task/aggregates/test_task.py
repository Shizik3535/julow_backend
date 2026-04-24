"""Unit-тесты для агрегата Task (Task BC)."""

from datetime import date

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.value_objects.task_priority import TaskPriority
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.domain.value_objects.task_status import TaskStatus
from app.context.task.domain.value_objects.task_progress import TaskProgress
from app.context.task.domain.value_objects.effort_estimate import EffortEstimate
from app.context.task.domain.value_objects.actual_effort import ActualEffort
from app.context.task.domain.value_objects.effort_unit import EffortUnit
from app.context.task.domain.value_objects.label import Label
from app.context.task.domain.value_objects.relation_type import RelationType
from app.context.task.domain.value_objects.recurrence_config import RecurrenceConfig
from app.context.task.domain.value_objects.recurrence_pattern import RecurrencePattern
from app.context.task.domain.events.task_events import (
    TaskCreated,
    TaskInfoChanged,
    TaskArchived,
    TaskRestored,
    TaskDeleted,
    TaskStatusChanged,
    TaskAssigned,
    TaskUnassigned,
    TaskPriorityChanged,
    TaskTypeChanged,
    TaskMoved,
    TaskMovedToSprint,
    TaskRemovedFromSprint,
    TaskMovedToEpic,
    TaskRemovedFromEpic,
    ChecklistAdded,
    ChecklistRemoved,
    ChecklistItemAdded,
    ChecklistItemToggled,
    ChecklistItemAssigned,
    TaskRelationAdded,
    TaskRelationRemoved,
    TaskProgressUpdated,
    TaskEffortUpdated,
    TaskWatcherAdded,
    TaskWatcherRemoved,
    TaskAttachmentAdded,
    TaskAttachmentRemoved,
    TaskCustomFieldChanged,
)
from app.context.task.domain.exceptions.task_exceptions import (
    TaskArchivedException,
    CannotRelateTaskToSelfException,
    DuplicateRelationException,
    DuplicateWatcherException,
    DuplicateLabelException,
    EffortUnitMismatchException,
    ChecklistNotFoundException,
    ChecklistItemNotFoundException,
)
from tests.factories import IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskCreation:
    def test_create_with_defaults(self, new_task: Task) -> None:
        assert new_task.status == TaskStatus.ACTIVE
        assert new_task.priority == TaskPriority.NONE
        assert new_task.progress == TaskProgress(value=0)
        assert new_task.assignee_ids == []
        assert new_task.labels == []
        assert new_task.checklists == []
        assert new_task.relations == []
        assert new_task.watchers == []
        assert new_task.attachments == []
        assert new_task.custom_fields == {}
        assert new_task.sprint_id is None
        assert new_task.recurrence is None

    def test_create_sets_title_project_type_reporter(self, new_task: Task, any_project_id: Id, any_reporter_id: Id) -> None:
        assert new_task.title == "Test Task"
        assert new_task.project_id == any_project_id
        assert new_task.task_type == TaskType.TASK
        assert new_task.reporter_id == any_reporter_id

    def test_create_with_parent_and_epic(self, any_project_id: Id, any_reporter_id: Id) -> None:
        parent_id = IdFactory()
        epic_id = IdFactory()
        task = Task.create(
            title="Sub-task",
            project_id=any_project_id,
            task_type=TaskType.SUBTASK,
            reporter_id=any_reporter_id,
            parent_task_id=parent_id,
            epic_id=epic_id,
        )
        assert task.parent_task_id == parent_id
        assert task.epic_id == epic_id

    def test_create_emits_task_created(self, new_task: Task) -> None:
        events = new_task.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskCreated)
        assert events[0].title == "Test Task"
        assert events[0].task_type == TaskType.TASK

    def test_create_from_template(self, any_project_id: Id, any_reporter_id: Id) -> None:
        labels = [Label(name="bug"), Label(name="urgent")]
        checklists_data = []
        custom_fields = {"env": "prod"}
        task = Task.create_from_template(
            template_name="Bug Report",
            template_type=TaskType.BUG,
            template_labels=labels,
            template_checklists=checklists_data,
            template_custom_fields=custom_fields,
            project_id=any_project_id,
            reporter_id=any_reporter_id,
        )
        assert task.title == "Bug Report"
        assert task.task_type == TaskType.BUG
        assert len(task.labels) == 2
        assert task.custom_fields == {"env": "prod"}

    def test_create_from_template_emits_task_created(self, any_project_id: Id, any_reporter_id: Id) -> None:
        task = Task.create_from_template(
            template_name="Bug Report",
            template_type=TaskType.BUG,
            template_labels=[],
            template_checklists=[],
            template_custom_fields={},
            project_id=any_project_id,
            reporter_id=any_reporter_id,
        )
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskCreated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Информация
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskUpdateInfo:
    def test_update_title(self, task: Task) -> None:
        task.update_info(title="New Title")
        assert task.title == "New Title"

    def test_update_info_emits_event(self, task: Task) -> None:
        task.update_info(title="New Title")
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskInfoChanged) for e in events)
        event = next(e for e in events if isinstance(e, TaskInfoChanged))
        assert "title" in event.changed_fields

    def test_update_info_no_change_no_event(self, task: Task) -> None:
        task.update_info(title="Test Task")
        events = task.clear_domain_events()
        assert not any(isinstance(e, TaskInfoChanged) for e in events)

    def test_update_info_multiple_fields(self, task: Task) -> None:
        task.update_info(title="New", description=RichText(content="desc"), start_date=date(2026, 1, 1))
        events = task.clear_domain_events()
        event = next(e for e in events if isinstance(e, TaskInfoChanged))
        assert "title" in event.changed_fields
        assert "description" in event.changed_fields
        assert "start_date" in event.changed_fields

    def test_update_info_when_archived_raises(self, archived_task: Task) -> None:
        with pytest.raises(TaskArchivedException):
            archived_task.update_info(title="New")


# ═══════════════════════════════════════════════════════════════════════════
# Workflow статус
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskChangeStatus:
    def test_change_status(self, task: Task) -> None:
        new_status_id = IdFactory()
        task.change_status(new_status_id)
        assert task.status_id == new_status_id

    def test_change_status_emits_event(self, task: Task) -> None:
        new_status_id = IdFactory()
        task.change_status(new_status_id)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskStatusChanged) for e in events)
        event = next(e for e in events if isinstance(e, TaskStatusChanged))
        assert event.new_status_id == str(new_status_id)

    def test_change_status_when_archived_raises(self, archived_task: Task) -> None:
        with pytest.raises(TaskArchivedException):
            archived_task.change_status(IdFactory())


# ═══════════════════════════════════════════════════════════════════════════
# Приоритет / Тип
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskPriorityAndType:
    def test_change_priority(self, task: Task) -> None:
        task.change_priority(TaskPriority.HIGH)
        assert task.priority == TaskPriority.HIGH

    def test_change_priority_emits_event(self, task: Task) -> None:
        task.change_priority(TaskPriority.HIGH)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskPriorityChanged) for e in events)

    def test_change_type(self, task: Task) -> None:
        task.change_type(TaskType.BUG)
        assert task.task_type == TaskType.BUG

    def test_change_type_emits_event(self, task: Task) -> None:
        task.change_type(TaskType.BUG)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskTypeChanged) for e in events)

    def test_change_priority_when_archived_raises(self, archived_task: Task) -> None:
        with pytest.raises(TaskArchivedException):
            archived_task.change_priority(TaskPriority.HIGH)


# ═══════════════════════════════════════════════════════════════════════════
# Исполнители
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskAssignment:
    def test_assign_user(self, task: Task, any_assignee_id: Id) -> None:
        task.assign(any_assignee_id)
        assert any_assignee_id in task.assignee_ids

    def test_assign_emits_event(self, task: Task, any_assignee_id: Id) -> None:
        task.assign(any_assignee_id)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskAssigned) for e in events)

    def test_assign_duplicate_is_noop(self, task: Task, any_assignee_id: Id) -> None:
        task.assign(any_assignee_id)
        task.clear_domain_events()
        task.assign(any_assignee_id)
        assert task.assignee_ids.count(any_assignee_id) == 1
        events = task.clear_domain_events()
        assert not any(isinstance(e, TaskAssigned) for e in events)

    def test_unassign_user(self, task: Task, any_assignee_id: Id) -> None:
        task.assign(any_assignee_id)
        task.clear_domain_events()
        task.unassign(any_assignee_id)
        assert any_assignee_id not in task.assignee_ids

    def test_unassign_emits_event(self, task: Task, any_assignee_id: Id) -> None:
        task.assign(any_assignee_id)
        task.clear_domain_events()
        task.unassign(any_assignee_id)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskUnassigned) for e in events)

    def test_unassign_nonexistent_is_noop(self, task: Task) -> None:
        task.unassign(IdFactory())
        events = task.clear_domain_events()
        assert not any(isinstance(e, TaskUnassigned) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Прогресс
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskProgress:
    def test_update_progress(self, task: Task) -> None:
        task.update_progress(TaskProgress(value=75))
        assert task.progress == TaskProgress(value=75)

    def test_update_progress_emits_event(self, task: Task) -> None:
        task.update_progress(TaskProgress(value=75))
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskProgressUpdated) for e in events)

    def test_compute_progress_from_checklists(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        task.add_checklist_item(cl.id, text="Step 1")
        task.add_checklist_item(cl.id, text="Step 2")
        task.add_checklist_item(cl.id, text="Step 3")
        task.add_checklist_item(cl.id, text="Step 4")
        task.clear_domain_events()
        task.toggle_checklist_item(cl.id, task.checklists[0].items[0].id)
        task.toggle_checklist_item(cl.id, task.checklists[0].items[1].id)
        task.clear_domain_events()
        task.compute_progress_from_checklists()
        assert task.progress == TaskProgress(value=50)

    def test_compute_progress_no_checklists_is_noop(self, task: Task) -> None:
        task.compute_progress_from_checklists()
        assert task.progress == TaskProgress(value=0)


# ═══════════════════════════════════════════════════════════════════════════
# Усилие
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskEffort:
    def test_set_effort_estimate(self, task: Task) -> None:
        estimate = EffortEstimate(value=8.0, unit=EffortUnit.HOURS)
        task.set_effort_estimate(estimate)
        assert task.effort_estimate == estimate

    def test_set_effort_estimate_emits_event(self, task: Task) -> None:
        task.set_effort_estimate(EffortEstimate(value=8.0, unit=EffortUnit.HOURS))
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskEffortUpdated) for e in events)

    def test_set_effort_estimate_unit_mismatch_raises(self, task: Task) -> None:
        task.set_actual_effort(ActualEffort(value=5.0, unit=EffortUnit.HOURS))
        with pytest.raises(EffortUnitMismatchException):
            task.set_effort_estimate(EffortEstimate(value=8.0, unit=EffortUnit.STORY_POINTS))

    def test_set_actual_effort(self, task: Task) -> None:
        effort = ActualEffort(value=5.0, unit=EffortUnit.HOURS)
        task.set_actual_effort(effort)
        assert task.actual_effort == effort

    def test_set_actual_effort_unit_mismatch_raises(self, task: Task) -> None:
        task.set_effort_estimate(EffortEstimate(value=8.0, unit=EffortUnit.HOURS))
        with pytest.raises(EffortUnitMismatchException):
            task.set_actual_effort(ActualEffort(value=5.0, unit=EffortUnit.DAYS))


# ═══════════════════════════════════════════════════════════════════════════
# Метки
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskLabels:
    def test_add_label(self, task: Task) -> None:
        task.add_label(Label(name="bug"))
        assert any(l.name == "bug" for l in task.labels)

    def test_add_duplicate_label_raises(self, task: Task) -> None:
        task.add_label(Label(name="bug"))
        with pytest.raises(DuplicateLabelException):
            task.add_label(Label(name="bug"))

    def test_remove_label(self, task: Task) -> None:
        task.add_label(Label(name="bug"))
        task.remove_label("bug")
        assert not any(l.name == "bug" for l in task.labels)


# ═══════════════════════════════════════════════════════════════════════════
# Перемещение
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskMove:
    def test_move(self, task: Task) -> None:
        column_id = IdFactory()
        task.move(column_id=column_id, position=2.5)
        assert task.order.position == 2.5
        assert task.order.column_id == column_id

    def test_move_emits_event(self, task: Task) -> None:
        task.move(column_id=IdFactory(), position=1.0)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskMoved) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Жизненный цикл
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskLifecycle:
    def test_archive(self, task: Task) -> None:
        task.archive()
        assert task.status == TaskStatus.ARCHIVED

    def test_archive_emits_event(self, task: Task) -> None:
        task.archive()
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskArchived) for e in events)

    def test_archive_when_not_active_is_noop(self, archived_task: Task) -> None:
        archived_task.archive()
        events = archived_task.clear_domain_events()
        assert not any(isinstance(e, TaskArchived) for e in events)

    def test_restore(self, archived_task: Task) -> None:
        archived_task.restore()
        assert archived_task.status == TaskStatus.ACTIVE

    def test_restore_emits_event(self, archived_task: Task) -> None:
        archived_task.restore()
        events = archived_task.clear_domain_events()
        assert any(isinstance(e, TaskRestored) for e in events)

    def test_restore_when_not_archived_is_noop(self, task: Task) -> None:
        task.restore()
        events = task.clear_domain_events()
        assert not any(isinstance(e, TaskRestored) for e in events)

    def test_soft_delete(self, task: Task) -> None:
        task.soft_delete()
        assert task.status == TaskStatus.DELETED

    def test_soft_delete_emits_event(self, task: Task) -> None:
        task.soft_delete()
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskDeleted) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Связи
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskRelations:
    def test_add_relation(self, task: Task) -> None:
        related_id = IdFactory()
        task.add_relation(related_task_id=related_id, relation_type=RelationType.BLOCKS, created_by=IdFactory())
        assert len(task.relations) == 1
        assert task.relations[0].related_task_id == related_id

    def test_add_relation_emits_event(self, task: Task) -> None:
        task.add_relation(related_task_id=IdFactory(), relation_type=RelationType.BLOCKS, created_by=IdFactory())
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskRelationAdded) for e in events)

    def test_add_relation_to_self_raises(self, task: Task) -> None:
        with pytest.raises(CannotRelateTaskToSelfException):
            task.add_relation(related_task_id=task.id, relation_type=RelationType.RELATES_TO, created_by=IdFactory())

    def test_add_duplicate_relation_raises(self, task: Task) -> None:
        related_id = IdFactory()
        task.add_relation(related_task_id=related_id, relation_type=RelationType.BLOCKS, created_by=IdFactory())
        with pytest.raises(DuplicateRelationException):
            task.add_relation(related_task_id=related_id, relation_type=RelationType.BLOCKS, created_by=IdFactory())

    def test_remove_relation(self, task: Task) -> None:
        related_id = IdFactory()
        task.add_relation(related_task_id=related_id, relation_type=RelationType.BLOCKS, created_by=IdFactory())
        task.clear_domain_events()
        task.remove_relation(related_task_id=related_id, relation_type=RelationType.BLOCKS)
        assert len(task.relations) == 0

    def test_remove_relation_emits_event(self, task: Task) -> None:
        related_id = IdFactory()
        task.add_relation(related_task_id=related_id, relation_type=RelationType.BLOCKS, created_by=IdFactory())
        task.clear_domain_events()
        task.remove_relation(related_task_id=related_id, relation_type=RelationType.BLOCKS)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskRelationRemoved) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Чек-листы
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskChecklists:
    def test_add_checklist(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        assert len(task.checklists) == 1
        assert task.checklists[0].title == "Steps"

    def test_add_checklist_emits_event(self, task: Task) -> None:
        task.add_checklist("Steps")
        events = task.clear_domain_events()
        assert any(isinstance(e, ChecklistAdded) for e in events)

    def test_remove_checklist(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        task.clear_domain_events()
        task.remove_checklist(cl.id)
        assert len(task.checklists) == 0

    def test_remove_checklist_emits_event(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        task.clear_domain_events()
        task.remove_checklist(cl.id)
        events = task.clear_domain_events()
        assert any(isinstance(e, ChecklistRemoved) for e in events)

    def test_remove_nonexistent_checklist_raises(self, task: Task) -> None:
        with pytest.raises(ChecklistNotFoundException):
            task.remove_checklist(IdFactory())

    def test_add_checklist_item(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        task.clear_domain_events()
        task.add_checklist_item(cl.id, text="Step 1")
        assert len(task.checklists[0].items) == 1
        assert task.checklists[0].items[0].text == "Step 1"

    def test_add_checklist_item_emits_event(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        task.clear_domain_events()
        task.add_checklist_item(cl.id, text="Step 1")
        events = task.clear_domain_events()
        assert any(isinstance(e, ChecklistItemAdded) for e in events)

    def test_add_checklist_item_to_missing_checklist_raises(self, task: Task) -> None:
        with pytest.raises(ChecklistNotFoundException):
            task.add_checklist_item(IdFactory(), text="Step 1")

    def test_toggle_checklist_item(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        task.add_checklist_item(cl.id, text="Step 1")
        item_id = task.checklists[0].items[0].id
        task.clear_domain_events()
        task.toggle_checklist_item(cl.id, item_id)
        assert task.checklists[0].items[0].is_checked is True

    def test_toggle_checklist_item_emits_event(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        task.add_checklist_item(cl.id, text="Step 1")
        item_id = task.checklists[0].items[0].id
        task.clear_domain_events()
        task.toggle_checklist_item(cl.id, item_id)
        events = task.clear_domain_events()
        assert any(isinstance(e, ChecklistItemToggled) for e in events)

    def test_toggle_checklist_item_missing_raises(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        with pytest.raises(ChecklistItemNotFoundException):
            task.toggle_checklist_item(cl.id, IdFactory())

    def test_assign_checklist_item(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        task.add_checklist_item(cl.id, text="Step 1")
        item_id = task.checklists[0].items[0].id
        assignee_id = IdFactory()
        task.clear_domain_events()
        task.assign_checklist_item(cl.id, item_id, assignee_id)
        assert task.checklists[0].items[0].assignee_id == assignee_id

    def test_assign_checklist_item_emits_event(self, task: Task) -> None:
        cl = task.add_checklist("Steps")
        task.add_checklist_item(cl.id, text="Step 1")
        item_id = task.checklists[0].items[0].id
        task.clear_domain_events()
        task.assign_checklist_item(cl.id, item_id, IdFactory())
        events = task.clear_domain_events()
        assert any(isinstance(e, ChecklistItemAssigned) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Спринт / Эпик
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskSprintAndEpic:
    def test_assign_to_sprint(self, task: Task) -> None:
        sprint_id = IdFactory()
        task.assign_to_sprint(sprint_id)
        assert task.sprint_id == sprint_id

    def test_assign_to_sprint_emits_event(self, task: Task) -> None:
        sprint_id = IdFactory()
        task.assign_to_sprint(sprint_id)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskMovedToSprint) for e in events)

    def test_remove_from_sprint(self, task: Task) -> None:
        task.assign_to_sprint(IdFactory())
        task.clear_domain_events()
        task.remove_from_sprint()
        assert task.sprint_id is None

    def test_remove_from_sprint_emits_event(self, task: Task) -> None:
        task.assign_to_sprint(IdFactory())
        task.clear_domain_events()
        task.remove_from_sprint()
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskRemovedFromSprint) for e in events)

    def test_assign_to_epic(self, task: Task) -> None:
        epic_id = IdFactory()
        task.assign_to_epic(epic_id)
        assert task.epic_id == epic_id

    def test_assign_to_epic_emits_event(self, task: Task) -> None:
        epic_id = IdFactory()
        task.assign_to_epic(epic_id)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskMovedToEpic) for e in events)

    def test_remove_from_epic(self, task: Task) -> None:
        task.assign_to_epic(IdFactory())
        task.clear_domain_events()
        task.remove_from_epic()
        assert task.epic_id is None

    def test_remove_from_epic_emits_event(self, task: Task) -> None:
        task.assign_to_epic(IdFactory())
        task.clear_domain_events()
        task.remove_from_epic()
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskRemovedFromEpic) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Наблюдатели
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskWatchers:
    def test_add_watcher(self, task: Task) -> None:
        user_id = IdFactory()
        task.add_watcher(user_id)
        assert any(w.user_id == user_id for w in task.watchers)

    def test_add_watcher_emits_event(self, task: Task) -> None:
        task.add_watcher(IdFactory())
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskWatcherAdded) for e in events)

    def test_add_duplicate_watcher_raises(self, task: Task) -> None:
        user_id = IdFactory()
        task.add_watcher(user_id)
        with pytest.raises(DuplicateWatcherException):
            task.add_watcher(user_id)

    def test_remove_watcher(self, task: Task) -> None:
        user_id = IdFactory()
        task.add_watcher(user_id)
        task.clear_domain_events()
        task.remove_watcher(user_id)
        assert not any(w.user_id == user_id for w in task.watchers)

    def test_remove_watcher_emits_event(self, task: Task) -> None:
        user_id = IdFactory()
        task.add_watcher(user_id)
        task.clear_domain_events()
        task.remove_watcher(user_id)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskWatcherRemoved) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Вложения
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskAttachments:
    def test_add_attachment(self, task: Task) -> None:
        file_id = IdFactory()
        task.add_attachment(file_id=file_id, filename="doc.pdf", size_bytes=1024, uploaded_by=IdFactory())
        assert len(task.attachments) == 1
        assert task.attachments[0].file_id == file_id

    def test_add_attachment_emits_event(self, task: Task) -> None:
        task.add_attachment(file_id=IdFactory(), filename="doc.pdf", size_bytes=1024, uploaded_by=IdFactory())
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskAttachmentAdded) for e in events)

    def test_remove_attachment(self, task: Task) -> None:
        file_id = IdFactory()
        task.add_attachment(file_id=file_id, filename="doc.pdf", size_bytes=1024, uploaded_by=IdFactory())
        task.clear_domain_events()
        task.remove_attachment(file_id)
        assert len(task.attachments) == 0

    def test_remove_attachment_emits_event(self, task: Task) -> None:
        file_id = IdFactory()
        task.add_attachment(file_id=file_id, filename="doc.pdf", size_bytes=1024, uploaded_by=IdFactory())
        task.clear_domain_events()
        task.remove_attachment(file_id)
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskAttachmentRemoved) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Кастомные поля
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskCustomFields:
    def test_set_custom_field(self, task: Task) -> None:
        task.set_custom_field("env", "prod")
        assert task.custom_fields["env"] == "prod"

    def test_set_custom_field_emits_event(self, task: Task) -> None:
        task.set_custom_field("env", "prod")
        events = task.clear_domain_events()
        assert any(isinstance(e, TaskCustomFieldChanged) for e in events)

    def test_set_custom_field_overwrite(self, task: Task) -> None:
        task.set_custom_field("env", "dev")
        task.clear_domain_events()
        task.set_custom_field("env", "prod")
        events = task.clear_domain_events()
        event = next(e for e in events if isinstance(e, TaskCustomFieldChanged))
        assert event.old_value == "dev"
        assert event.new_value == "prod"

    def test_remove_custom_field(self, task: Task) -> None:
        task.set_custom_field("env", "prod")
        task.clear_domain_events()
        task.remove_custom_field("env")
        assert "env" not in task.custom_fields

    def test_remove_custom_field_emits_event(self, task: Task) -> None:
        task.set_custom_field("env", "prod")
        task.clear_domain_events()
        task.remove_custom_field("env")
        events = task.clear_domain_events()
        event = next(e for e in events if isinstance(e, TaskCustomFieldChanged))
        assert event.old_value == "prod"
        assert event.new_value == ""

    def test_remove_nonexistent_custom_field_is_noop(self, task: Task) -> None:
        task.remove_custom_field("nonexistent")
        events = task.clear_domain_events()
        assert not any(isinstance(e, TaskCustomFieldChanged) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Повторение
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskRecurrence:
    def test_set_recurrence(self, task: Task) -> None:
        config = RecurrenceConfig(pattern=RecurrencePattern.WEEKLY, interval=2)
        task.set_recurrence(config)
        assert task.recurrence == config

    def test_remove_recurrence(self, task: Task) -> None:
        task.set_recurrence(RecurrenceConfig())
        task.remove_recurrence()
        assert task.recurrence is None
