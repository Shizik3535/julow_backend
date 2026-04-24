from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.identity.application.dto.role_dto import RoleDTO


class IdentityRoleProvider(ABC):
    """
    Outboard-порт: предоставляет данные ролей другим BC.

    Другие BC инжектируют этот порт через DI для синхронного
    получения данных о ролях из Identity BC.

    Реализация находится в infrastructure-слое Identity BC.
    """

    @abstractmethod
    async def get_role(self, role_id: str) -> RoleDTO | None:
        """
        Получить роль по ID.

        Аргументы:
            role_id: Идентификатор роли.

        Возвращает:
            RoleDTO или None, если не найдена.
        """

    @abstractmethod
    async def get_user_roles(self, user_id: str) -> list[RoleDTO]:
        """
        Получить все роли пользователя.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            Список RoleDTO.
        """
