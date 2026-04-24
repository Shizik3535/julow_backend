from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.notification import Notification


class NotificationRepository(RepositoryPort[Notification]):
    """Порт репозитория для агрегата Notification."""

    @abstractmethod
    async def get_unread_by_user(self, user_id: Id) -> list[Notification]:
        """Найти непрочитанные уведомления пользователя."""

    @abstractmethod
    async def get_by_user(self, user_id: Id) -> list[Notification]:
        """Найти все уведомления пользователя."""

    @abstractmethod
    async def count_unread(self, user_id: Id) -> int:
        """Подсчитать непрочитанные уведомления."""

    @abstractmethod
    async def mark_all_read(self, user_id: Id) -> int:
        """Пометить все уведомления пользователя как прочитанные. Возвращает количество."""
