from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class OrganizationPort(ABC):
    """
    Inboard-порт: получение данных организации из Organization BC.

    Workspace BC использует этот порт для проверки существования
    организации при создании workspace, привязанного к организации.
    Реализация — адаптер в infrastructure, делегирующий в
    OrganizationProvider (outboard Organization BC).
    """

    @abstractmethod
    async def org_exists(self, org_id: str) -> bool:
        """Проверить существование организации."""

    @abstractmethod
    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        """Получить данные организации (dict) или None."""
