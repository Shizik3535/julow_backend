from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.context.analytics.application.dto.analytics_query_dto import AnalyticsResultDTO
from app.context.analytics.application.exceptions.analytics_app_exceptions import (
    AnalyticsQueryExecutionException,
    UnsupportedDataSourceException,
)
from app.context.analytics.application.ports.query_execution.analytics_query_executor_port import (
    AnalyticsQueryExecutorPort,
)
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.bounded_context_ref import (
    BoundedContextRef,
)
from app.context.analytics.infrastructure.query_execution.analytics_bc_resolver import (
    AnalyticsBCResolver,
)

logger = get_logger(__name__)


class AnalyticsQueryExecutorAdapter(AnalyticsQueryExecutorPort):
    """
    Реализация ``AnalyticsQueryExecutorPort``.

    Маршрутизирует ``AnalyticsQuery`` по ``query.bounded_context``
    к зарегистрированному ``AnalyticsBCResolver``. Domain слой
    Analytics BC не импортирует другие BC; ACL изолирован в резолверах.

    Поведение:
        - Если резолвер для BC не зарегистрирован — бросает
          ``UnsupportedDataSourceException`` (501);
        - Если резолвер бросает исключение — оборачиваем в
          ``AnalyticsQueryExecutionException`` (502), кроме случая,
          когда это уже UnsupportedDataSourceException.
    """

    def __init__(self, resolvers: Iterable[AnalyticsBCResolver] | None = None) -> None:
        self._resolvers: dict[BoundedContextRef, AnalyticsBCResolver] = {}
        for resolver in resolvers or ():
            self.register(resolver)

    def register(self, resolver: AnalyticsBCResolver) -> None:
        """Зарегистрировать резолвер. Перезаписывает предыдущий для того же BC."""
        self._resolvers[resolver.bounded_context] = resolver

    async def execute(
        self, query: AnalyticsQuery, workspace_id: str
    ) -> AnalyticsResultDTO:
        bc = query.bounded_context
        resolver = self._resolvers.get(bc)
        if resolver is None:
            logger.warning(
                "Analytics resolver not registered",
                bounded_context=bc.value,
                data_source=query.data_source.value,
            )
            raise UnsupportedDataSourceException(data_source=query.data_source.value)

        try:
            return await resolver.execute(query=query, workspace_id=workspace_id)
        except UnsupportedDataSourceException:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Analytics resolver failed",
                bounded_context=bc.value,
                data_source=query.data_source.value,
                error=str(exc),
            )
            raise AnalyticsQueryExecutionException(detail=str(exc)) from exc


def empty_result(query: AnalyticsQuery) -> AnalyticsResultDTO:
    """Утилита-фабрика пустого результата (используется в резолверах-заглушках)."""
    columns: list[str] = []
    for d in query.dimensions:
        columns.append(d.alias or d.field)
    for m in query.metrics:
        columns.append(m.alias or f"{m.aggregation.value}_{m.field}")
    return AnalyticsResultDTO(
        data_source=query.data_source.value,
        bounded_context=query.bounded_context.value,
        columns=columns,
        rows=[],
        total=0,
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
    )
