from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.value_objects.project_view_config import ProjectViewConfig


@dataclass
class ProjectView(BaseEntity):
    """
    Сущность представления проекта.

    Принадлежит агрегату Board.

    Атрибуты:
        name: Название представления.
        config: Конфигурация представления.
        is_default: Является ли представлением по умолчанию.
        is_shared: Общее ли представление.
        owner_id: ID владельца (None — общее).
    """

    name: str = ""
    config: ProjectViewConfig = field(default_factory=ProjectViewConfig)
    is_default: bool = False
    is_shared: bool = True
    owner_id: Id | None = None
