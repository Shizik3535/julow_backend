from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.notification.application.dto.notification_preferences_dto import NotificationPreferencesDTO


class NotificationPreferencesProvider(ABC):
    """Outboard-порт: предоставляет настройки уведомлений другим BC."""

    @abstractmethod
    async def get_preferences(self, user_id: str) -> NotificationPreferencesDTO | None:
        """Получить настройки уведомлений пользователя."""

    @abstractmethod
    async def should_deliver(self, user_id: str, notification_type: str, channel: str, scope_id: str | None = None) -> bool:
        """Проверить, нужно ли доставлять уведомление."""

    @abstractmethod
    async def is_dnd_active(self, user_id: str) -> bool:
        """Проверить, активен ли режим «Не беспокоить» для пользователя."""
