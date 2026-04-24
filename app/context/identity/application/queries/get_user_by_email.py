from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.email_vo import Email
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.domain.exceptions.user_exceptions import UserNotFoundException
from app.context.identity.domain.repositories.user_repository import UserRepository


class GetUserByEmailQuery(BaseQuery):
    """
    Запрос пользователя по email.

    Атрибуты:
        email: Email-адрес пользователя.
    """

    email: str


class GetUserByEmailHandler(BaseQueryHandler[GetUserByEmailQuery, UserDTO]):
    """
    Обработчик запроса пользователя по email.
    """

    def __init__(self, user_repo: UserRepository) -> None:
        super().__init__()
        self._user_repo = user_repo

    async def handle(self, query: GetUserByEmailQuery) -> UserDTO:
        user = await self._user_repo.get_by_email(Email(query.email))
        if user is None:
            raise UserNotFoundException(query.email)

        return UserDTO(
            id=str(user.id),
            email=user.email.value,
            status=user.status.value,
            role_ids=[str(rid) for rid in user.role_ids],
            is_email_confirmed=user.is_email_confirmed,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
