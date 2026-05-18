from __future__ import annotations

from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.application.dto.user_dto import UserDTO
from app.context.identity.application.ports.integration.outboard.identity_user_provider import (
    IdentityUserProvider,
)
from app.context.identity.domain.repositories.user_repository import UserRepository


class UserProviderAdapter(IdentityUserProvider):
    """
    Реализация IdentityUserProvider.

    Предоставляет данные пользователей другим BC
    через синхронный DI-порт.
    """

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def get_user(self, user_id: str) -> UserDTO | None:
        user = await self._user_repo.get_by_id(Id.from_string(user_id))
        if user is None:
            return None
        return UserDTO(
            id=str(user.id),
            email=user.email.value,
            status=user.status.value,
            role_ids=[str(rid) for rid in user.role_ids],
            is_email_confirmed=user.is_email_confirmed,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def get_users(self, user_ids: list[str]) -> list[UserDTO]:
        result: list[UserDTO] = []
        for uid in user_ids:
            dto = await self.get_user(uid)
            if dto is not None:
                result.append(dto)
        return result

    async def get_user_by_email(self, email: str) -> UserDTO | None:
        # Email VO нормализует (trim/lowercase) сам; на сторону БД мы
        # отдаём уже нормализованное значение. Если строка не валидна
        # как email, возвращаем None — это «такого пользователя нет»,
        # а не «исключение» (валидация бизнес-смысла лежит в Identity BC).
        try:
            normalized = Email(email)
        except Exception:  # noqa: BLE001 — invalid email format treated as not-found
            return None
        user = await self._user_repo.get_by_email(normalized)
        if user is None:
            return None
        return UserDTO(
            id=str(user.id),
            email=user.email.value,
            status=user.status.value,
            role_ids=[str(rid) for rid in user.role_ids],
            is_email_confirmed=user.is_email_confirmed,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
