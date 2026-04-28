from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.notification.application.dto.notification_dto import NotificationDTO


class NotificationListDTO(BaseDTO):
    """
    DTO списка уведомлений.

    Атрибуты:
        items: Список уведомлений.
        total: Общее количество.
        unread_count: Количество непрочитанных.
    """

    items: list[NotificationDTO] = []
    total: int = 0
    unread_count: int = 0
