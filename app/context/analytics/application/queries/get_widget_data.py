from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsResultDTO
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.application.ports.query_execution.analytics_query_executor_port import (
    AnalyticsQueryExecutorPort,
)
from app.context.analytics.domain.exceptions.dashboard_exceptions import (
    DashboardNotFoundException,
    WidgetNotFoundException,
)
from app.context.analytics.domain.repositories.dashboard_repository import DashboardRepository


class GetWidgetDataQuery(BaseQuery):
    """Получить данные виджета (выполняет AnalyticsQuery через executor port)."""

    caller_id: str
    dashboard_id: str
    widget_id: str


class GetWidgetDataHandler(BaseQueryHandler[GetWidgetDataQuery, AnalyticsResultDTO]):
    REQUIRED_PERMISSION = "analytics.read"

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        query_executor: AnalyticsQueryExecutorPort,
        permission_checker: AnalyticsPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = dashboard_repo
        self._executor = query_executor
        self._permission_checker = permission_checker

    async def handle(self, query: GetWidgetDataQuery) -> AnalyticsResultDTO:
        dashboard = await self._repo.get_by_id(Id.from_string(query.dashboard_id))
        if dashboard is None:
            raise DashboardNotFoundException(id=query.dashboard_id)
        widget_id = Id.from_string(query.widget_id)
        widget = next((w for w in dashboard.widgets if w.id == widget_id), None)
        if widget is None or widget.config is None:
            raise WidgetNotFoundException(id=query.widget_id)

        is_owner = str(dashboard.owner_id) == query.caller_id
        is_shared = any(str(s.user_id) == query.caller_id for s in dashboard.shares)
        if not is_owner and not is_shared:
            if dashboard.workspace_id is None:
                raise AnalyticsAccessDeniedException("widget", query.widget_id)
            await self._permission_checker.require_permission(
                user_id=query.caller_id,
                workspace_id=str(dashboard.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )

        return await self._executor.execute(
            query=widget.config.query,
            workspace_id=str(dashboard.workspace_id) if dashboard.workspace_id else "",
        )
