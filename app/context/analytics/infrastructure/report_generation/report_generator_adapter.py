from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id

from app.context.analytics.application.dto.report_dto import ReportJobDTO
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    ReportScheduleRequiredException,
    ReportWorkspaceRequiredException,
)
from app.context.analytics.application.ports.report_generation.report_generator_port import (
    ReportGeneratorPort,
)
from app.context.analytics.application.ports.report_generation.report_render_scheduler_port import (
    ReportRenderSchedulerPort,
)
from app.context.analytics.domain.exceptions.report_exceptions import (
    ReportNotFoundException,
)
from app.context.analytics.domain.repositories.report_repository import ReportRepository
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.export_format import ExportFormat
from app.context.analytics.domain.value_objects.report_type import ReportType
from app.context.analytics.infrastructure.persistence.mappers._query_serialization import (
    analytics_query_to_json,
)
from app.context.analytics.infrastructure.persistence.repositories.sql_report_job_repository import (
    SqlReportJobRepository,
)


class ReportGeneratorAdapter(ReportGeneratorPort):
    """
    Реализация ``ReportGeneratorPort``.

    Сохраняет состояние задания в таблице ``analytics_report_jobs`` со
    статусом ``pending`` и делегирует фактический рендеринг в фоновый
    ``ReportRenderSchedulerPort``.

    Фоновый воркер выполняет:
        1. читает задание из ``analytics_report_jobs`` по ``job_id``;
        2. через ``AnalyticsQueryExecutorPort.execute`` получает
           ``AnalyticsResultDTO``;
        3. рендерит результат в файл нужного формата (PDF/Excel/CSV/...);
        4. **сохраняет файл через ``FileAttachmentPort`` Analytics BC**
           (inboard) → ``FileAttachmentProvider`` FileStorage BC (outboard).
           Это обязательный путь — нельзя писать в S3 напрямую: иначе
           обходится квота workspace, антивирус, ``FileUploaded``-события
           и регистрация ``File`` агрегата в FileStorage BC.
        5. обновляет статус задания: ``SqlReportJobRepository.mark_completed``
           с ``download_url`` от FileStorage и ``expires_at``;
        6. на агрегате ``Report`` вызывает ``mark_generated`` /
           ``mark_exported`` → события ``ReportGenerated`` /
           ``ReportExported`` уходят в Analytics event bus.

    Сам ``ReportGeneratorAdapter`` шаги 2–6 не выполняет — он только
    регистрирует задание и ставит его в очередь.
    """

    def __init__(
        self,
        report_repo: ReportRepository,
        job_repo: SqlReportJobRepository,
        render_scheduler: ReportRenderSchedulerPort,
    ) -> None:
        self._report_repo = report_repo
        self._job_repo = job_repo
        self._scheduler = render_scheduler

    async def request_generation(
        self,
        *,
        workspace_id: str,
        report_type: ReportType,
        query: AnalyticsQuery,
        format: ExportFormat,
        requested_by: str,
        report_id: str | None = None,
        scheduled_report_id: str | None = None,
    ) -> ReportJobDTO:
        job = await self._job_repo.add(
            workspace_id=workspace_id,
            report_type=report_type.value,
            format=format.value,
            query_payload=analytics_query_to_json(query),
            requested_by=requested_by,
            report_id=report_id,
            scheduled_report_id=scheduled_report_id,
        )
        await self._scheduler.schedule(job_id=job.id)
        return job

    async def get_job(self, job_id: str) -> ReportJobDTO | None:
        return await self._job_repo.get_by_id(job_id)

    async def send_scheduled_now(
        self,
        *,
        workspace_id: str,
        report_id: str,
        requested_by: str,
    ) -> ReportJobDTO:
        report = await self._report_repo.get_by_id(Id.from_string(report_id))
        if report is None:
            raise ReportNotFoundException(id=report_id)
        if report.schedule is None:
            raise ReportScheduleRequiredException(report_id=report_id)
        # Workspace-less отчёты не могут участвовать в scheduled-канале:
        # job-таблица требует non-null `workspace_id`, и квота/permissions
        # должны проверяться против реального workspace отчёта, а не того,
        # что прилетело от вызывающего слоя.
        if report.workspace_id is None:
            raise ReportWorkspaceRequiredException(report_id=report_id)

        # `workspace_id` параметр оставлен для контракта порта, но игнорируем:
        # источник истины — `report.workspace_id`.
        _ = workspace_id
        fmt = report.last_export_format or ExportFormat.PDF
        return await self.request_generation(
            workspace_id=str(report.workspace_id),
            report_type=report.report_type,
            query=report.query,
            format=fmt,
            requested_by=requested_by,
            report_id=report_id,
            scheduled_report_id=report_id,
        )
