from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.identity.application.dto.user_dto import UserDTO


class IdentityUserProvider(ABC):
    """
    Outboard-порт: предоставляет данные пользователей другим BC.

    Другие BC инжектируют этот порт через DI для синхронного
    получения данных о пользователях из Identity BC.

    Реализация находится в infrastructure-слое Identity BC.
    """

    @abstractmethod
    async def get_user(self, user_id: str) -> UserDTO | None:
        """
        Получить пользователя по ID.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            UserDTO или None, если не найден.
        """

    @abstractmethod
    async def get_users(self, user_ids: list[str]) -> list[UserDTO]:
        """
        Получить список пользователей по ID.

        Аргументы:
            user_ids: Список идентификаторов пользователей.

        Возвращает:
            Список UserDTO.
        """
