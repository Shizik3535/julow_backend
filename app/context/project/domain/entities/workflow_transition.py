from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.value_objects.automation_trigger import AutomationTrigger


@dataclass
class WorkflowTransition(BaseEntity):
    """
    Сущность перехода между статусами workflow.

    Принадлежит агрегату Board.

    Атрибуты:
        from_status_id: ID исходного статуса.
        to_status_id: ID целевого статуса.
        name: Название перехода.
        trigger: Триггер автоматизации (None — ручной).
        required_permission: Разрешение для перехода (None — без ограничения).
    """

    from_status_id: Id = field(default_factory=Id.generate)
    to_status_id: Id = field(default_factory=Id.generate)
    name: str = ""
    trigger: AutomationTrigger | None = None
    required_permission: str | None = None
