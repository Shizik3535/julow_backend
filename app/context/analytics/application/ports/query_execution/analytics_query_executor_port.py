from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsResultDTO
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery


class AnalyticsQueryExecutorPort(ABC):
    """
    Концерн-порт исполнения аналитического запроса.

    Реализация на infrastructure-слое инкапсулирует ACL ко всем
    остальным BC (Task/Project/TimeTracking/Communication/...) и
    маршрутизирует запрос по `query.data_source.bounded_context`
    к соответствующему адаптеру/SQL/материализованной view.

    Контракт:
        - Принимает `AnalyticsQuery` (domain VO);
        - Возвращает `AnalyticsResultDTO` (плоский результат);
        - При неподдерживаемом источнике — `UnsupportedDataSourceException`;
        - При ошибке выполнения — `AnalyticsQueryExecutionException`.
    """

    @abstractmethod
    async def execute(self, query: AnalyticsQuery, workspace_id: str) -> AnalyticsResultDTO:
        """Выполнить запрос в контексте workspace."""
