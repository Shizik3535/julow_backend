from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.organization.application.dto.org_member_dto import OrgMemberDTO


class OrganizationMembershipProvider(ABC):
    """
    Outboard-порт: предоставляет данные о членстве в организациях другим BC.

    Profile BC и другие потребляют этот порт для проверки членства
    и получения информации о роли пользователя в организации.
    """

    @abstractmethod
    async def is_member(self, user_id: str, org_id: str) -> bool:
        """
        Проверить, состоит ли пользователь в организации.

        Аргументы:
            user_id: Идентификатор пользователя.
            org_id: Идентификатор организации.

        Возвращает:
            True, если пользователь состоит в организации.
        """

    @abstractmethod
    async def get_member_role(self, user_id: str, org_id: str) -> str | None:
        """
        Получить роль пользователя в организации.

        Аргументы:
            user_id: Идентификатор пользователя.
            org_id: Идентификатор организации.

        Возвращает:
            ID роли или None, если пользователь не состоит в организации.
        """

    @abstractmethod
    async def get_members(self, org_id: str) -> list[OrgMemberDTO]:
        """
        Получить всех участников организации.

        Аргументы:
            org_id: Идентификатор организации.

        Возвращает:
            Список DTO участников.
        """

    @abstractmethod
    async def org_exists(self, org_id: str) -> bool:
        """
        Проверить, существует ли организация.

        Аргументы:
            org_id: Идентификатор организации.

        Возвращает:
            True, если организация существует.
        """
