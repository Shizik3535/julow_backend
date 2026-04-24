from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_entity import BaseEntity
from app.context.project.domain.value_objects.automation_trigger import AutomationTrigger
from app.context.project.domain.value_objects.automation_action import AutomationAction


@dataclass
class AutomationRule(BaseEntity):
    """
    Сущность правила автоматизации.

    Принадлежит агрегату Board.

    Атрибуты:
        name: Название правила.
        trigger: Триггер.
        action: Действие.
        action_params: Параметры действия.
        is_enabled: Включено ли правило.
    """

    name: str = ""
    trigger: AutomationTrigger = AutomationTrigger.STATUS_CHANGED
    action: AutomationAction = AutomationAction.SEND_NOTIFICATION
    action_params: dict[str, str] = field(default_factory=dict)
    is_enabled: bool = True
