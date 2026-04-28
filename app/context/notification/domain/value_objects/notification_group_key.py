from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.value_objects.notification_type import NotificationType


@dataclass(frozen=True)
class NotificationGroupKey(ValueObject):
    """
    Value Object для ключа группировки уведомлений.

    Однотипные уведомления за window_minutes группируются.
    Например, 5 комментариев к одной задаче за 5 минут → 1 уведомление.

    Атрибуты:
        type: Тип уведомления.
        target_id: ID целевого объекта (задача, проект и т.д.).
        window_minutes: Окно группировки в минутах.
    """

    type: NotificationType = NotificationType.TASK_ASSIGNED
    target_id: Id | None = None
    window_minutes: int = 5

    def __post_init__(self) -> None:
        if self.window_minutes < 1:
            raise ValueError("window_minutes должен быть >= 1")

    def __str__(self) -> str:
        target = str(self.target_id) if self.target_id else "none"
        return f"{self.type.value}:{target}:{self.window_minutes}"
