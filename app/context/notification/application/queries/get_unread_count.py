from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.notification.domain.repositories.notification_repository import NotificationRepository
from app.context.notification.application.dto.unread_count_dto import UnreadCountDTO


class GetUnreadCountQuery(BaseQuery):
    """
    Запрос количества непрочитанных уведомлений.

    Атрибуты:
        user_id: ID пользователя.
    """

    user_id: str


class GetUnreadCountHandler(BaseQueryHandler[GetUnreadCountQuery, UnreadCountDTO]):
    """Обработчик запроса количества непрочитанных уведомлений."""

    def __init__(self, notification_repo: NotificationRepository) -> None:
        super().__init__()
        self._repo = notification_repo

    async def handle(self, query: GetUnreadCountQuery) -> UnreadCountDTO:
        user_id = Id.from_string(query.user_id)
        total = await self._repo.count_unread(user_id)

        # Получаем все уведомления для подсчёта по workspace
        notifications = await self._repo.get_unread_by_user(user_id)
        by_workspace: dict[str, int] = {}
        for n in notifications:
            if n.workspace_id is not None:
                ws_key = str(n.workspace_id)
                by_workspace[ws_key] = by_workspace.get(ws_key, 0) + 1

        return UnreadCountDTO(total=total, by_workspace=by_workspace)
