from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.analytics.domain.aggregates.dashboard_template import DashboardTemplate


class DashboardTemplateRepository(RepositoryPort[DashboardTemplate]):
    @abstractmethod
    async def get_system_templates(self) -> list[DashboardTemplate]: ...

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[DashboardTemplate]: ...

    @abstractmethod
    async def get_by_name(
        self, name: str, workspace_id: Id | None = None
    ) -> DashboardTemplate | None:
        """Найти шаблон по имени в заданной области видимости.

        ``workspace_id=None`` — искать среди системных шаблонов (они глобальны
        и имеют ``workspace_id is None``). Иначе — среди кастомных шаблонов
        указанного workspace. Имя не уникально между workspace'ами, поэтому
        этот параметр обязателен для корректного поиска.
        """

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[DashboardTemplate]: ...
