"""No-op адаптер ``ReportRenderSchedulerPort``.

Сам порт определён в application-слое
(``app.context.analytics.application.ports.report_generation``); здесь
лежит только инфраструктурная реализация для dev/CI окружений без
воркера.
"""
from __future__ import annotations

from app.core.logging import get_logger
from app.context.analytics.application.ports.report_generation.report_render_scheduler_port import (
    ReportRenderSchedulerPort,
)

logger = get_logger(__name__)


class NoopReportRenderScheduler(ReportRenderSchedulerPort):
    """No-op планировщик (только логирует факт постановки в очередь).

    Используется в средах без воркера (dev/CI). Задание остаётся в
    статусе ``pending`` до тех пор, пока его не подхватит реальный
    воркер или внешний сервис.
    """

    async def schedule(self, job_id: str) -> None:
        logger.info("Report render scheduled (noop)", job_id=job_id)
