from __future__ import annotations

from app.shared.application.base_query import BaseQuery
from app.shared.application.base_query_handler import BaseQueryHandler

from app.context.analytics.application.dto.report_dto import ReportJobDTO
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    ReportJobNotFoundException,
)
from app.context.analytics.application.ports.report_generation.report_generator_port import (
    ReportGeneratorPort,
)


class GetReportJobQuery(BaseQuery):
    """Получить статус задания на генерацию отчёта (job_id)."""

    caller_id: str
    job_id: str


class GetReportJobHandler(BaseQueryHandler[GetReportJobQuery, ReportJobDTO]):
    def __init__(self, report_generator: ReportGeneratorPort) -> None:
        super().__init__()
        self._generator = report_generator

    async def handle(self, query: GetReportJobQuery) -> ReportJobDTO:
        job = await self._generator.get_job(query.job_id)
        if job is None:
            raise ReportJobNotFoundException(query.job_id)
        return job
