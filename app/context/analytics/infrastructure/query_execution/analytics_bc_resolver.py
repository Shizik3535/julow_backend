from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.analytics.application.dto.analytics_query_dto import AnalyticsResultDTO
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.bounded_context_ref import (
    BoundedContextRef,
)


class AnalyticsBCResolver(ABC):
    """
    Резолвер аналитических запросов одного BC.

    Каждый BC, который выступает источником данных аналитики, реализует
    собственный резолвер (ACL): он умеет переводить ``AnalyticsQuery``
    в SQL/материализованную view внутри своей схемы и возвращать
    плоский результат.

    Регистрируется в ``AnalyticsQueryExecutorAdapter`` по своему
    ``bounded_context``.
    """

    @property
    @abstractmethod
    def bounded_context(self) -> BoundedContextRef:
        """BC, который обслуживает этот резолвер."""

    @abstractmethod
    async def execute(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        """Выполнить запрос для указанного workspace."""
