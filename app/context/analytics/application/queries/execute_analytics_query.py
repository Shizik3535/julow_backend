from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler

from app.context.analytics.application.dto.analytics_query_dto import (
    AnalyticsQueryDTO,
    AnalyticsResultDTO,
)
from app.context.analytics.application.dto.mappers import analytics_query_from_dto
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    AnalyticsWorkspaceNotFoundException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.application.ports.integration.inboard.workspace_port import WorkspacePort
from app.context.analytics.application.ports.query_execution.analytics_query_executor_port import (
    AnalyticsQueryExecutorPort,
)


class ExecuteAnalyticsQueryQuery(BaseQuery):
    """Ad-hoc выполнение AnalyticsQuery (для preview/ad-hoc-аналитики)."""

    caller_id: str
    workspace_id: str
    query: AnalyticsQueryDTO


class ExecuteAnalyticsQueryHandler(
    BaseQueryHandler[ExecuteAnalyticsQueryQuery, AnalyticsResultDTO]
):
    REQUIRED_PERMISSION = "analytics.read"

    def __init__(
        self,
        query_executor: AnalyticsQueryExecutorPort,
        permission_checker: AnalyticsPermissionCheckerPort,
        workspace_port: WorkspacePort,
    ) -> None:
        super().__init__()
        self._executor = query_executor
        self._permission_checker = permission_checker
        self._workspace_port = workspace_port

    async def handle(self, query: ExecuteAnalyticsQueryQuery) -> AnalyticsResultDTO:
        if not await self._workspace_port.workspace_exists(query.workspace_id):
            raise AnalyticsWorkspaceNotFoundException(query.workspace_id)
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=query.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        domain_query = analytics_query_from_dto(query.query)
        return await self._executor.execute(domain_query, query.workspace_id)
