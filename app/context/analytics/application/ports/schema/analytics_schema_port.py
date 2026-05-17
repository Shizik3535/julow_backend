"""BC-специфичный порт: провайдер метаданных Analytics-схемы.

Analytics BC сам не знает о полях задач/проектов/time-entries —
это знание принадлежит соответствующим BC и резолверам в infrastructure-
слое. Application объявляет лишь контракт ("дайте мне описание
DataSource"), а конкретная реализация (статический реестр или
самообследование резолверов) живёт в infrastructure.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.analytics.application.dto.analytics_schema_dto import (
    AnalyticsSchemaDTO,
    DataSourceSchemaDTO,
    DataSourceSummaryDTO,
)


class AnalyticsSchemaPort(ABC):
    """Поставляет метаданные доступных ``DataSource`` и связанных enum'ов.

    Используется ``GetAnalyticsSchemaHandler`` для ответа на endpoint'ы
    ``/analytics/schema``, ``/analytics/data-sources`` и
    ``/analytics/data-sources/{source}``.
    """

    @abstractmethod
    def get_full_schema(self) -> AnalyticsSchemaDTO:
        """Полный реестр: все источники + глобальные enum'ы."""

    @abstractmethod
    def list_data_sources(self) -> list[DataSourceSummaryDTO]:
        """Краткий список поддерживаемых источников."""

    @abstractmethod
    def get_data_source_schema(self, data_source: str) -> DataSourceSchemaDTO | None:
        """Полная схема одного источника или ``None``, если не поддержан."""
