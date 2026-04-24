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
    async def get_by_name(self, name: str) -> DashboardTemplate | None: ...

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[DashboardTemplate]: ...
