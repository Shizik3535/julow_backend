from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.task.domain.value_objects.task_type import TaskType
from app.context.task.domain.value_objects.label import Label
from app.context.task.domain.entities.checklist import Checklist
from app.context.task.domain.events.task_template_events import (
    TaskTemplateCreated,
    TaskTemplateUpdated,
    TaskTemplateDeleted,
)
from app.context.task.domain.exceptions.task_template_exceptions import (
    CannotDeleteSystemTemplateException,
)


@dataclass
class TaskTemplate(AggregateRoot):
    """
    Корень агрегата шаблона задачи (Task BC).

    Предустановленные шаблоны (Bug Report, Feature Request, Spike, User Story, Task)
    с is_system=True. Кастомные шаблоны создаются на уровне проекта.

    Атрибуты:
        name: Название шаблона.
        description: Описание (форматированный текст).
        task_type: Тип задачи по умолчанию.
        default_labels: Метки по умолчанию.
        default_checklists: Чек-листы по умолчанию.
        default_custom_fields: Значения кастомных полей по умолчанию.
        is_system: Является ли шаблон системным.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    name: str = ""
    description: RichText | None = None
    task_type: TaskType = TaskType.TASK
    default_labels: list[Label] = field(default_factory=list)
    default_checklists: list[Checklist] = field(default_factory=list)
    default_custom_fields: dict[str, str] = field(default_factory=dict)
    is_system: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create_system(
        cls,
        name: str,
        task_type: TaskType,
        default_labels: list[Label] | None = None,
        default_checklists: list[Checklist] | None = None,
        default_custom_fields: dict[str, str] | None = None,
    ) -> TaskTemplate:
        """Создаёт системный шаблон."""
        template = cls(
            name=name,
            task_type=task_type,
            default_labels=default_labels or [],
            default_checklists=default_checklists or [],
            default_custom_fields=default_custom_fields or {},
            is_system=True,
        )
        template._register_event(TaskTemplateCreated(template_name=name))
        return template

    @classmethod
    def create_custom(
        cls,
        name: str,
        task_type: TaskType,
        default_labels: list[Label] | None = None,
        default_checklists: list[Checklist] | None = None,
        default_custom_fields: dict[str, str] | None = None,
    ) -> TaskTemplate:
        """Создаёт кастомный шаблон."""
        template = cls(
            name=name,
            task_type=task_type,
            default_labels=default_labels or [],
            default_checklists=default_checklists or [],
            default_custom_fields=default_custom_fields or {},
            is_system=False,
        )
        template._register_event(TaskTemplateCreated(template_name=name))
        return template

    def update(
        self,
        default_labels: list[Label] | None = None,
        default_checklists: list[Checklist] | None = None,
        default_custom_fields: dict[str, str] | None = None,
    ) -> None:
        if default_labels is not None:
            self.default_labels = default_labels
        if default_checklists is not None:
            self.default_checklists = default_checklists
        if default_custom_fields is not None:
            self.default_custom_fields = default_custom_fields
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(TaskTemplateUpdated(template_name=self.name))

    def assert_deletable(self) -> None:
        if self.is_system:
            raise CannotDeleteSystemTemplateException(name=self.name)

    def mark_deleted(self) -> None:
        self.assert_deletable()
        self._register_event(TaskTemplateDeleted(template_name=self.name))
