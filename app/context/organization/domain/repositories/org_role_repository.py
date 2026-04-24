from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.org_role import OrgRole


class OrgRoleRepository(RepositoryPort[OrgRole]):
    """
    Порт репозитория для агрегата OrgRole.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления ролями организации.
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> OrgRole | None:
        """Найти роль по названию."""

    @abstractmethod
    async def get_system_roles(self) -> list[OrgRole]:
        """Получить все системные роли (is_system=True)."""

    @abstractmethod
    async def get_by_org(self, org_id: Id) -> list[OrgRole]:
        """Получить все роли организации (системные + кастомные)."""

    @abstractmethod
    async def get_by_org_and_name(self, org_id: Id, name: str) -> OrgRole | None:
        """Найти роль организации по org_id и названию."""

    @abstractmethod
    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[OrgRole]:
        """Поиск ролей с опциональной фильтрацией."""
