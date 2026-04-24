from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.organization.application.dto.organization_dto import OrganizationDTO


class OrganizationProvider(ABC):
    """
    Outboard-порт: предоставляет данные организаций другим BC.

    Другие BC (Profile, Workspace и т.д.) потребляют этот порт
    через свои inboard-порты для получения данных об организациях.
    """

    @abstractmethod
    async def get_organization(self, org_id: str) -> OrganizationDTO | None:
        """
        Получить данные организации по ID.

        Аргументы:
            org_id: Идентификатор организации.

        Возвращает:
            DTO организации или None.
        """

    @abstractmethod
    async def organization_exists(self, org_id: str) -> bool:
        """
        Проверить, существует ли организация.

        Аргументы:
            org_id: Идентификатор организации.

        Возвращает:
            True, если организация существует.
        """
