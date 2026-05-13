from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler
from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.mappers import report_to_dto
from app.context.analytics.application.dto.report_dto import ReportDTO
from app.context.analytics.application.exceptions.authorization_exceptions import (
    AnalyticsAccessDeniedException,
)
from app.context.analytics.application.ports.authorization.analytics_permission_checker_port import (
    AnalyticsPermissionCheckerPort,
)
from app.context.analytics.domain.exceptions.report_exceptions import ReportNotFoundException
from app.context.analytics.domain.repositories.report_repository import ReportRepository


class GetReportQuery(BaseQuery):
    caller_id: str
    report_id: str


class GetReportHandler(BaseQueryHandler[GetReportQuery, ReportDTO]):
    REQUIRED_PERMISSION = "analytics.read"

    def __init__(
        self,
        report_repo: ReportRepository,
        permission_checker: AnalyticsPermissionCheckerPort,
    ) -> None:
        super().__init__()
        self._repo = report_repo
        self._permission_checker = permission_checker

    async def handle(self, query: GetReportQuery) -> ReportDTO:
        report = await self._repo.get_by_id(Id.from_string(query.report_id))
        if report is None:
            raise ReportNotFoundException(id=query.report_id)

        is_owner = str(report.owner_id) == query.caller_id
        is_shared = any(str(s.user_id) == query.caller_id for s in report.shares)
        if not is_owner and not is_shared and report.workspace_id is not None:
            has_perm = await self._permission_checker.has_permission(
                user_id=query.caller_id,
                workspace_id=str(report.workspace_id),
                permission=self.REQUIRED_PERMISSION,
            )
            if not has_perm:
                raise AnalyticsAccessDeniedException("report", query.report_id)

        return report_to_dto(report)
