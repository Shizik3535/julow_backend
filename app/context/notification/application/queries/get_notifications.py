from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.application.dto.notification_dto import NotificationDTO
from app.context.notification.application.dto.notification_list_dto import NotificationListDTO


class GetNotificationsQuery(BaseQuery):
    """
    Запрос списка уведомлений.

    Атрибуты:
        user_id: ID пользователя.
        workspace_id: ID workspace (опционально).
        notification_type: Тип уведомления (опционально).
        is_read: Фильтр по прочитанности (опционально).
        page: Номер страницы.
        limit: Размер страницы.
    """

    user_id: str
    workspace_id: str | None = None
    notification_type: str | None = None
    is_read: bool | None = None
    page: int = 1
    limit: int = 20


class GetNotificationsHandler(BaseQueryHandler[GetNotificationsQuery, NotificationListDTO]):
    """Обработчик запроса списка уведомлений."""

    def __init__(self, notification_repo: NotificationRepository) -> None:
        super().__init__()
        self._repo = notification_repo

    async def handle(self, query: GetNotificationsQuery) -> NotificationListDTO:
        user_id = Id.from_string(query.user_id)

        if query.workspace_id:
            workspace_id = Id.from_string(query.workspace_id)
            notifications = await self._repo.get_by_user_and_workspace(user_id, workspace_id)
        else:
            notifications = await self._repo.get_by_user(user_id)

        # Фильтрация
        if query.notification_type is not None:
            notifications = [n for n in notifications if n.notification_type.value == query.notification_type]
        if query.is_read is not None:
            notifications = [n for n in notifications if n.is_read == query.is_read]

        total = len(notifications)
        unread_count = sum(1 for n in notifications if not n.is_read)

        # Пагинация
        offset = (query.page - 1) * query.limit
        page_items = notifications[offset:offset + query.limit]

        items = [
            NotificationDTO(
                id=str(n.id),
                recipient_id=str(n.recipient_id),
                workspace_id=str(n.workspace_id) if n.workspace_id else None,
                notification_type=n.notification_type.value,
                title=n.title,
                body=n.body,
                priority=n.priority.value,
                data=n.data,
                channels=[ch.value for ch in n.channels],
                is_read=n.is_read,
                read_at=n.read_at,
                is_archived=n.is_archived,
                actor_id=str(n.actor_id) if n.actor_id else None,
                created_at=n.created_at,
            )
            for n in page_items
        ]

        return NotificationListDTO(items=items, total=total, unread_count=unread_count)
