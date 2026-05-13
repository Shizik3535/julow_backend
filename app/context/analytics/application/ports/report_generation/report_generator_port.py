from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.analytics.application.dto.report_dto import ReportJobDTO
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.export_format import ExportFormat
from app.context.analytics.domain.value_objects.report_type import ReportType


class ReportGeneratorPort(ABC):
    """
    Концерн-порт генерации отчётов.

    Инфраструктурная реализация:
        - принимает запрос на генерацию (типа отчёта, query, формат);
        - помещает задание в очередь/таблицу `report_jobs`;
        - возвращает `ReportJobDTO` со статусом ``pending`` и ``id`` задания;
        - фоновый воркер позже выполняет `AnalyticsQueryExecutorPort` + рендер
          в формат (PDF/Excel/CSV/PNG) и обновляет статус/`download_url`.

    Подписки/события (`ReportGenerationRequested/Completed/Failed`) публикуются
    реализацией адаптера. Application-слой к ним не привязан.
    """

    @abstractmethod
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
        """Поставить задание на генерацию; вернуть DTO задания со статусом."""

    @abstractmethod
    async def get_job(self, job_id: str) -> ReportJobDTO | None:
        """Получить статус задания."""

    @abstractmethod
    async def send_scheduled_now(
        self,
        *,
        workspace_id: str,
        report_id: str,
        requested_by: str,
    ) -> ReportJobDTO:
        """Запустить немедленную отправку scheduled-отчёта."""
