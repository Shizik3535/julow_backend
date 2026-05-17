from __future__ import annotations

from enum import Enum

from app.context.analytics.application.dto.analytics_query_dto import (
    AnalyticsQueryDTO,
    DateRangeDTO,
    DimensionDTO,
    FilterConfigDTO,
    MetricDefinitionDTO,
    SortConfigDTO,
)
from app.context.analytics.presentation.schemas.requests.analytics_requests import (
    AnalyticsQueryRequest,
)


def _enum_val(v: Enum | str | None) -> str | None:
    """Извлечь строковое значение из Enum или вернуть str как есть."""
    if v is None:
        return None
    return v.value if isinstance(v, Enum) else v


def query_request_to_dto(req: AnalyticsQueryRequest) -> AnalyticsQueryDTO:
    """Преобразовать AnalyticsQueryRequest (presentation) в AnalyticsQueryDTO (application)."""

    date_range_dto: DateRangeDTO | None = None
    if req.date_range is not None:
        date_range_dto = DateRangeDTO(
            start=req.date_range.start,
            end=req.date_range.end,
        )

    return AnalyticsQueryDTO(
        data_source=_enum_val(req.data_source),
        metrics=[
            MetricDefinitionDTO(
                field=m.field,
                aggregation=_enum_val(m.aggregation),
                alias=m.alias,
            )
            for m in req.metrics
        ],
        dimensions=[
            DimensionDTO(
                field=d.field,
                time_granularity=_enum_val(d.time_granularity),
                alias=d.alias,
            )
            for d in req.dimensions
        ],
        filters=[
            FilterConfigDTO(
                field=f.field,
                operator=_enum_val(f.operator),
                value=f.value,
                value_to=f.value_to,
            )
            for f in req.filters
        ],
        date_range=date_range_dto,
        sort=[
            SortConfigDTO(
                field=s.field,
                order=_enum_val(s.order),
            )
            for s in req.sort
        ],
        limit=req.limit,
        raw=req.raw,
    )
