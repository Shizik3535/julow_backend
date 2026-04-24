from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class TaskTemplateDTO(BaseDTO):
    """
    DTO шаблона задачи (Task BC).

    Атрибуты:
        id: Идентификатор.
        name: Название.
        description: Описание (dict).
        task_type: Тип задачи.
        default_labels: Метки по умолчанию.
        default_checklists: Чек-листы по умолчанию.
        default_custom_fields: Кастомные поля по умолчанию.
        is_system: Системный ли.
        created_at: Время создания.
        updated_at: Время обновления.
    """

    id: str
    name: str = ""
    description: dict[str, Any] | None = None
    task_type: str = "TASK"
    default_labels: list[dict[str, Any]] = []
    default_checklists: list[dict[str, Any]] = []
    default_custom_fields: dict[str, str] = {}
    is_system: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TaskTemplateListDTO(BaseDTO):
    """Список шаблонов задач с total."""

    items: list[TaskTemplateDTO]
    total: int
