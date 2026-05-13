from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.dashboard_dto import DashboardListDTO
from app.context.analytics.application.dto.mappers import dashboard_to_dto
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.repositories.dashboard_repository import DashboardRepository


class ListDashboardsByWorkspaceQuery(BaseQuery):
    """Список дашбордов workspace, видимых caller'у."""

    caller_id: str
    workspace_id: str


class ListDashboardsByWorkspaceHandler(
    BaseQueryHandler[ListDashboardsByWorkspaceQuery, DashboardListDTO]
):
    REQUIRED_PERMISSION = "analytics.read"

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = dashboard_repo
        self._permission_checker = permission_checker

    async def handle(self, query: ListDashboardsByWorkspaceQuery) -> DashboardListDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=query.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        dashboards = await self._repo.get_by_workspace(Id.from_string(query.workspace_id))
        items = [dashboard_to_dto(d) for d in dashboards]
        return DashboardListDTO(items=items, total=len(items))


class ListDashboardsSharedWithMeQuery(BaseQuery):
    """Дашборды, расшаренные с caller'ом."""

    caller_id: str


class ListDashboardsSharedWithMeHandler(
    BaseQueryHandler[ListDashboardsSharedWithMeQuery, DashboardListDTO]
):
    def __init__(self, dashboard_repo: DashboardRepository) -> None:
        super().__init__()
        self._repo = dashboard_repo

    async def handle(
        self, query: ListDashboardsSharedWithMeQuery
    ) -> DashboardListDTO:
        dashboards = await self._repo.get_shared_with_user(Id.from_string(query.caller_id))
        items = [dashboard_to_dto(d) for d in dashboards]
        return DashboardListDTO(items=items, total=len(items))
