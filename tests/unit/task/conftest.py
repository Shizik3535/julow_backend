"""
Task BC conftest — фикстуры для unit-тестов Task BC.

Содержит фабричные фикстуры для агрегатов и VOs,
используемых в нескольких тестовых модулях.
"""

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.context.task.domain.aggregates.task import Task
from app.context.task.domain.aggregates.task_template import TaskTemplate
from app.context.task.domain.aggregates.changelog import ChangelogEntry
from app.context.task.domain.value_objects.task_type import TaskType
from tests.factories import IdFactory


# ── Value Object фикстуры ─────────────────────────────────────────────────


@pytest.fixture
def any_project_id() -> Id:
    """Случайный Id проекта."""
    return IdFactory()


@pytest.fixture
def any_reporter_id() -> Id:
    """Случайный Id автора задачи."""
    return IdFactory()


@pytest.fixture
def any_assignee_id() -> Id:
    """Случайный Id исполнителя."""
    return IdFactory()


# ── Агрегат Task ──────────────────────────────────────────────────────────


@pytest.fixture
def new_task(any_project_id: Id, any_reporter_id: Id) -> Task:
    """Задача через Task.create()."""
    return Task.create(
        title="Test Task",
        project_id=any_project_id,
        task_type=TaskType.TASK,
        reporter_id=any_reporter_id,
    )


@pytest.fixture
def task(new_task: Task) -> Task:
    """Задача с очищенными событиями."""
    new_task.clear_domain_events()
    return new_task


@pytest.fixture
def archived_task(task: Task) -> Task:
    """Задача в статусе ARCHIVED."""
    task.archive()
    task.clear_domain_events()
    return task


# ── Агрегат TaskTemplate ──────────────────────────────────────────────────


@pytest.fixture
def new_system_template() -> TaskTemplate:
    """Системный шаблон через TaskTemplate.create_system()."""
    return TaskTemplate.create_system(
        name="Bug Report",
        task_type=TaskType.BUG,
    )


@pytest.fixture
def system_template(new_system_template: TaskTemplate) -> TaskTemplate:
    """Системный шаблон с очищенными событиями."""
    new_system_template.clear_domain_events()
    return new_system_template


@pytest.fixture
def new_custom_template() -> TaskTemplate:
    """Кастомный шаблон через TaskTemplate.create_custom()."""
    return TaskTemplate.create_custom(
        name="My Template",
        task_type=TaskType.TASK,
    )


@pytest.fixture
def custom_template(new_custom_template: TaskTemplate) -> TaskTemplate:
    """Кастомный шаблон с очищенными событиями."""
    new_custom_template.clear_domain_events()
    return new_custom_template


# ── Агрегат ChangelogEntry ────────────────────────────────────────────────


@pytest.fixture
def new_changelog_entry(any_project_id: Id, any_reporter_id: Id) -> ChangelogEntry:
    """Запись истории через ChangelogEntry.create()."""
    return ChangelogEntry.create(
        task_id=any_project_id,
        field_name="status",
        old_value="open",
        new_value="closed",
        changed_by=any_reporter_id,
    )


@pytest.fixture
def changelog_entry(new_changelog_entry: ChangelogEntry) -> ChangelogEntry:
    """Запись истории с очищенными событиями."""
    new_changelog_entry.clear_domain_events()
    return new_changelog_entry
