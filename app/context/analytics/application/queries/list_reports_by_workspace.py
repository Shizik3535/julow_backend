from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.mappers import report_to_dto
from app.context.analytics.application.dto.report_dto import ReportListDTO
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.repositories.report_repository import ReportRepository
from app.context.analytics.domain.value_objects.bounded_context_ref import BoundedContextRef
from app.context.analytics.domain.value_objects.report_type import ReportType


class ListReportsByWorkspaceQuery(BaseQuery):
    """Список отчётов workspace с опциональным фильтром по типу/BC."""

    caller_id: str
    workspace_id: str
    report_type: str | None = None  # ReportType.value
    bounded_context: str | None = None  # BoundedContextRef.value


class ListReportsByWorkspaceHandler(
    BaseQueryHandler[ListReportsByWorkspaceQuery, ReportListDTO]
):
    REQUIRED_PERMISSION = "analytics.read"

    def __init__(
        self,
        report_repo: ReportRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = report_repo
        self._permission_checker = permission_checker

    async def handle(self, query: ListReportsByWorkspaceQuery) -> ReportListDTO:
        await self._permission_checker.require_permission(
            user_id=query.caller_id,
            workspace_id=query.workspace_id,
            permission=self.REQUIRED_PERMISSION,
        )
        ws_id = Id.from_string(query.workspace_id)

        if query.report_type:
            reports = await self._repo.get_by_type(ReportType(query.report_type), ws_id)
        elif query.bounded_context:
            reports = await self._repo.get_by_bounded_context(
                BoundedContextRef(query.bounded_context), ws_id
            )
        else:
            reports = await self._repo.get_by_workspace(ws_id)
        items = [report_to_dto(r) for r in reports]
        return ReportListDTO(items=items, total=len(items))


class ListScheduledReportsQuery(BaseQuery):
    """Список запланированных отчётов (для воркера/админа). caller — admin."""

    caller_id: str


class ListScheduledReportsHandler(
    BaseQueryHandler[ListScheduledReportsQuery, ReportListDTO]
):
    def __init__(self, report_repo: ReportRepository) -> None:
        super().__init__()
        self._repo = report_repo

    async def handle(self, query: ListScheduledReportsQuery) -> ReportListDTO:
        reports = await self._repo.get_scheduled_reports()
        items = [report_to_dto(r) for r in reports]
        return ReportListDTO(items=items, total=len(items))
