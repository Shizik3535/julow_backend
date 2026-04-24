from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.session_dto import SessionDTO
from app.context.identity.application.dto.session_list_dto import SessionListDTO
from app.context.identity.domain.repositories.session_repository import SessionRepository


class GetActiveSessionsQuery(BaseQuery):
    """
    Запрос активных сессий пользователя.

    Атрибуты:
        user_id: Идентификатор пользователя.
    """

    user_id: str


class GetActiveSessionsHandler(BaseQueryHandler[GetActiveSessionsQuery, SessionListDTO]):
    """
    Обработчик запроса активных сессий пользователя.
    """

    def __init__(self, session_repo: SessionRepository) -> None:
        super().__init__()
        self._session_repo = session_repo

    async def handle(self, query: GetActiveSessionsQuery) -> SessionListDTO:
        sessions = await self._session_repo.get_active_by_user(Id.from_string(query.user_id))

        items = [
            SessionDTO(
                id=str(s.id),
                user_id=str(s.user_id),
                device_info=s.device_info.user_agent,
                ip_address=s.ip_address.value,
                status=s.status.value,
                is_remember_me=s.is_remember_me,
                created_at=s.created_at,
                expires_at=s.expires_at,
            )
            for s in sessions
        ]

        return SessionListDTO(items=items, total=len(items))
