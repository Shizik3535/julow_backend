from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.color_vo import Color
from app.context.project.domain.value_objects.workflow_status_category import WorkflowStatusCategory


@dataclass
class WorkflowStatus(BaseEntity):
    """
    Сущность кастомного статуса задачи.

    Принадлежит агрегату Board.

    Атрибуты:
        name: Название статуса.
        color: Цвет статуса (из shared kernel).
        icon: Иконка.
        order: Порядок.
        is_default: Является ли статусом по умолчанию.
        category: Категория статуса.
    """

    name: str = ""
    color: Color | None = None
    icon: str | None = None
    order: int = 0
    is_default: bool = False
    category: WorkflowStatusCategory = WorkflowStatusCategory.TODO
