"""Application-порт планирования фоновой генерации отчёта.

Инфраструктурная абстракция — позволяет ``ReportGeneratorPort`` адаптеру
не завязываться напрямую на Celery/RQ/Arq. Реальная реализация
(``CeleryReportRenderScheduler`` и т. п.) планирует задачу в очередь;
``NoopReportRenderScheduler`` (см. infrastructure-слой) — no-op для
тестов и сценариев без воркера.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class ReportRenderSchedulerPort(ABC):
    """Планировщик фоновой задачи рендеринга отчёта."""

    @abstractmethod
    async def schedule(self, job_id: str) -> None:
        """Поставить задачу рендеринга в очередь."""
