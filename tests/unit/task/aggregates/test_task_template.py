"""Unit-тесты для агрегата TaskTemplate (Task BC)."""

import pytest

from app.context.task.domain.aggregates.task_template import TaskTemplate
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.domain.value_objects.label import Label
from app.context.task.domain.events.task_template_events import (
    TaskTemplateCreated,
    TaskTemplateUpdated,
    TaskTemplateDeleted,
)
from app.context.task.domain.exceptions.task_template_exceptions import (
    CannotDeleteSystemTemplateException,
)


# ═══════════════════════════════════════════════════════════════════════════
# Создание
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskTemplateCreation:
    def test_create_system(self, new_system_template: TaskTemplate) -> None:
        assert new_system_template.is_system is True
        assert new_system_template.name == "Bug Report"
        assert new_system_template.task_type == TaskType.BUG

    def test_create_system_emits_event(self, new_system_template: TaskTemplate) -> None:
        events = new_system_template.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskTemplateCreated)
        assert events[0].template_name == "Bug Report"

    def test_create_custom(self, new_custom_template: TaskTemplate) -> None:
        assert new_custom_template.is_system is False
        assert new_custom_template.name == "My Template"
        assert new_custom_template.task_type == TaskType.TASK

    def test_create_custom_emits_event(self, new_custom_template: TaskTemplate) -> None:
        events = new_custom_template.clear_domain_events()
        assert any(isinstance(e, TaskTemplateCreated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Обновление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskTemplateUpdate:
    def test_update_labels(self, custom_template: TaskTemplate) -> None:
        labels = [Label(name="bug"), Label(name="urgent")]
        custom_template.update(default_labels=labels)
        assert len(custom_template.default_labels) == 2

    def test_update_checklists(self, custom_template: TaskTemplate) -> None:
        custom_template.update(default_checklists=[])
        assert custom_template.default_checklists == []

    def test_update_custom_fields(self, custom_template: TaskTemplate) -> None:
        custom_template.update(default_custom_fields={"env": "prod"})
        assert custom_template.default_custom_fields == {"env": "prod"}

    def test_update_emits_event(self, custom_template: TaskTemplate) -> None:
        custom_template.update(default_labels=[Label(name="new")])
        events = custom_template.clear_domain_events()
        assert any(isinstance(e, TaskTemplateUpdated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Удаление
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTaskTemplateDeletion:
    def test_mark_deleted_custom(self, custom_template: TaskTemplate) -> None:
        custom_template.mark_deleted()
        events = custom_template.clear_domain_events()
        assert any(isinstance(e, TaskTemplateDeleted) for e in events)

    def test_assert_deletable_system_raises(self, system_template: TaskTemplate) -> None:
        with pytest.raises(CannotDeleteSystemTemplateException):
            system_template.assert_deletable()

    def test_mark_deleted_system_raises(self, system_template: TaskTemplate) -> None:
        with pytest.raises(CannotDeleteSystemTemplateException):
            system_template.mark_deleted()
