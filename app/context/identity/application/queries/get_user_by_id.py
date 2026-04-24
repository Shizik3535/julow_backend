from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_repository import UserRepository


class GetUserByIdQuery(BaseQuery):
    """
    Запрос пользователя по ID.

    Атрибуты:
        user_id: Идентификатор пользователя.
    """

    user_id: str


class GetUserByIdHandler(BaseQueryHandler[GetUserByIdQuery, UserDTO]):
    """
    Обработчик запроса пользователя по ID.
    """

    def __init__(self, user_repo: UserRepository) -> None:
        super().__init__()
        self._user_repo = user_repo

    async def handle(self, query: GetUserByIdQuery) -> UserDTO:
        user = await self._user_repo.get_by_id(Id.from_string(query.user_id))
        if user is None:
            raise UserNotFoundException(query.user_id)

        return UserDTO(
            id=str(user.id),
            email=user.email.value,
            status=user.status.value,
            role_ids=[str(rid) for rid in user.role_ids],
            is_email_confirmed=user.is_email_confirmed,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
