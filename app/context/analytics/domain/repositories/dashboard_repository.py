from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.analytics.domain.aggregates.dashboard import Dashboard


class DashboardRepository(RepositoryPort[Dashboard]):
    @abstractmethod
    async def get_by_owner(self, owner_id: Id) -> list[Dashboard]: ...

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[Dashboard]: ...

    @abstractmethod
    async def get_shared_with_user(self, user_id: Id) -> list[Dashboard]: ...

    @abstractmethod
    async def get_default_by_workspace(self, workspace_id: Id) -> Dashboard | None: ...

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[Dashboard]: ...
