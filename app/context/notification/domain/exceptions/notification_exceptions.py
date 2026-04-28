from __future__ import annotations

from app.shared.domain.exceptions import EntityNotFoundException
from app.shared.domain.base_exceptions import DomainException


class NotificationNotFoundException(EntityNotFoundException):
    """Уведомление не найдено."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Notification", id=id)


class NotificationPreferencesNotFoundException(EntityNotFoundException):
    """Настройки уведомлений не найдены."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="NotificationPreferences", id=id)


class InvalidDndScheduleException(DomainException):
    """Некорректное расписание DND."""

    def __init__(self, message: str = "Некорректное расписание «Не беспокоить»") -> None:
        super().__init__(message)


class InvalidDigestConfigException(DomainException):
    """Некорректная конфигурация дайджеста."""

    def __init__(self, message: str = "Некорректная конфигурация дайджеста") -> None:
        super().__init__(message)


class DeviceTokenNotFoundException(EntityNotFoundException):
    """Токен устройства не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="DeviceToken", id=id)
