from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class NotificationTypeDTO(BaseDTO):
    """
    DTO типа уведомления.

    Атрибуты:
        type: Значение типа (например "task_assigned").
        label: Человекочитаемое название.
        default_channels: Каналы по умолчанию.
    """

    type: str = ""
    label: str = ""
    default_channels: list[str] = []


class NotificationTypeListDTO(BaseDTO):
    """Список типов уведомлений."""

    items: list[NotificationTypeDTO] = []
