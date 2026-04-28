from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.aggregates.notification import Notification
from app.context.notification.domain.value_objects.notification_group_key import NotificationGroupKey
from app.context.notification.domain.value_objects.notification_type import NotificationType


class NotificationRepository(RepositoryPort[Notification]):
    """Порт репозитория для агрегата Notification."""

    @abstractmethod
    async def get_unread_by_user(self, user_id: Id) -> list[Notification]:
        """Найти непрочитанные уведомления пользователя."""

    @abstractmethod
    async def get_by_user(self, user_id: Id) -> list[Notification]:
        """Найти все уведомления пользователя."""

    @abstractmethod
    async def get_by_user_and_workspace(self, user_id: Id, workspace_id: Id) -> list[Notification]:
        """Найти уведомления пользователя в workspace."""

    @abstractmethod
    async def count_unread(self, user_id: Id) -> int:
        """Подсчитать непрочитанные уведомления."""

    @abstractmethod
    async def count_unread_by_workspace(self, user_id: Id, workspace_id: Id) -> int:
        """Подсчитать непрочитанные уведомления в workspace."""

    @abstractmethod
    async def mark_all_read(self, user_id: Id, workspace_id: Id | None = None) -> int:
        """Пометить все уведомления пользователя как прочитанные. Если указан workspace_id, только в этом workspace. Возвращает количество."""

    @abstractmethod
    async def get_by_group_key(self, group_key: NotificationGroupKey, recipient_id: Id | None = None) -> list[Notification]:
        """Найти уведомления по ключу группировки. Если указан recipient_id, фильтрует по получателю."""

    @abstractmethod
    async def get_archived(self, user_id: Id) -> list[Notification]:
        """Найти архивированные уведомления пользователя."""

    @abstractmethod
    async def has_unread_by_type_and_target(
        self,
        recipient_id: Id,
        notification_type: NotificationType,
        target_key: str,
    ) -> bool:
        """
        Проверить наличие unread уведомления данного типа для target (task_id/project_id).

        Используется для дедупликации — чтобы не создавать повторное уведомление
        того же типа для того же объекта тому же пользователю.
        """
