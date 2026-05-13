from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.dashboard_dto import DashboardDTO
from app.context.analytics.application.dto.mappers import dashboard_to_dto
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    DashboardNotFoundException,
)
from app.context.analytics.domain.repositories.dashboard_repository import DashboardRepository


class GetDashboardQuery(BaseQuery):
    """Получить дашборд по ID. Видим владельцу/шарингу/при permission."""

    caller_id: str
    dashboard_id: str


class GetDashboardHandler(BaseQueryHandler[GetDashboardQuery, DashboardDTO]):
    REQUIRED_PERMISSION = "analytics.read"

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = dashboard_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetDashboardQuery) -> DashboardDTO:
        dashboard = await self._repo.get_by_id(Id.from_string(query.dashboard_id))
        if dashboard is None:
            raise DashboardNotFoundException(id=query.dashboard_id)

        is_owner = str(dashboard.owner_id) == query.caller_id
        is_shared_with_me = any(
            str(s.user_id) == query.caller_id for s in dashboard.shares
        )
        if not is_owner and not is_shared_with_me and dashboard.workspace_id is not None:
            has_perm = await self._permission_checker.has_permission(
                user_id=query.caller_id,
                workspace_id=str(dashboard.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
            if not has_perm:
                raise AnalyticsAccessDeniedException("dashboard", query.dashboard_id)

        return dashboard_to_dto(dashboard)
