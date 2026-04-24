from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.analytics.domain.aggregates.report import Report
from app.context.analytics.domain.value_objects.report_type import ReportType
from app.context.analytics.domain.value_objects.data_source import DataSource


class ReportRepository(RepositoryPort[Report]):
    @abstractmethod
    async def get_by_owner(self, owner_id: Id) -> list[Report]: ...

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[Report]: ...

    @abstractmethod
    async def get_shared_with_user(self, user_id: Id) -> list[Report]: ...

    @abstractmethod
    async def get_scheduled_reports(self) -> list[Report]: ...

    @abstractmethod
    async def get_by_type(self, report_type: ReportType, workspace_id: Id) -> list[Report]: ...

    @abstractmethod
    async def get_by_data_source(self, data_source: DataSource, workspace_id: Id) -> list[Report]: ...

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[Report]: ...
