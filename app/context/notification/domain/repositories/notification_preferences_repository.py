from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.notification_preferences import NotificationPreferences


class NotificationPreferencesRepository(RepositoryPort[NotificationPreferences]):
    """Порт репозитория для агрегата NotificationPreferences."""

    @abstractmethod
    async def get_by_user_id(self, user_id: Id) -> NotificationPreferences | None:
        """Найти настройки уведомлений по ID пользователя."""
