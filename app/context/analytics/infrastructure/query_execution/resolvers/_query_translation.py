"""
Вспомогательные функции перевода ``AnalyticsQuery`` → параметры
outboard-провайдеров и сборки ``AnalyticsResultDTO``.

Используется всеми резолверами Analytics BC (``WorkspaceAnalyticsResolver``,
``ProjectAnalyticsResolver``, ``TaskAnalyticsResolver``,
``TimeTrackingAnalyticsResolver``). Не зависит от конкретного BC.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.context.analytics.application.dto.analytics_query_dto import (
    AnalyticsResultDTO,
    AnalyticsResultRowDTO,
)
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.filter_config import FilterConfig
from app.context.analytics.domain.value_objects.filter_operator import FilterOperator


# Имя «технической» bucket-колонки, которую провайдеры возвращают для
# измерений с заданным ``time_granularity``.
TIME_BUCKET_COLUMN = "date_bucket"


def iso_now() -> str:
    """Текущий UTC-таймстемп в ISO-формате (для generated_at)."""
    return datetime.now(tz=timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


def filter_values(filters: list[FilterConfig], field: str) -> list[str] | None:
    """Собрать включающие значения фильтра по конкретному ``field``.

    Возвращает:
        - ``None`` — фильтра для этого поля нет;
        - ``list[str]`` — список значений (пустой, если фильтр существует,
          но его оператор не является включающим, например ``GTE``/``LTE``).

    Поддерживает операторы ``EQ`` (одно значение), ``IN``
    (запятая-разделитель в ``value``).
    Для ``NOT_IN`` используйте ``filter_excluded_values``.
    Остальные операторы для перечисляемых фильтров игнорируются (вызывающий
    код должен явно обработать их через ``filter_first``/``filter_bool``).
    """
    out: list[str] = []
    found = False
    for f in filters:
        if f.field != field:
            continue
        found = True
        if f.operator == FilterOperator.EQ:
            if f.value is not None:
                out.append(f.value)
        elif f.operator == FilterOperator.IN:
            if f.value is not None:
                out.extend(_split_csv(f.value))
    return out if found else None


def filter_excluded_values(
    filters: list[FilterConfig], field: str
) -> list[str] | None:
    """Собрать исключающие значения фильтра (``NOT_IN``) по конкретному ``field``.

    Возвращает:
        - ``None`` — ``NOT_IN`` фильтра для этого поля нет;
        - ``list[str]`` — список значений для исключения.
    """
    out: list[str] = []
    found = False
    for f in filters:
        if f.field != field:
            continue
        if f.operator == FilterOperator.NOT_IN:
            found = True
            out.extend(_split_csv(f.value))
    return out if found else None


def filter_first(filters: list[FilterConfig], field: str) -> str | None:
    """Вернуть первое значение фильтра по полю (``EQ`` / первый ``IN``)."""
    values = filter_values(filters, field)
    if values is None or len(values) == 0:
        return None
    return values[0]


def filter_bool(filters: list[FilterConfig], field: str) -> bool | None:
    """Парсинг булева фильтра по полю.

    Принимает ``"true"``/``"false"`` / ``"1"``/``"0"`` / ``"yes"``/``"no"``
    (case-insensitive).

    Возвращает:
        - ``None`` — фильтра нет или значение не распознано;
        - ``True`` — явно истинное значение;
        - ``False`` — явно ложное значение (``"false"``/``"0"``/``"no"``).
    """
    raw = filter_first(filters, field)
    if raw is None:
        return None
    normalized = raw.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    return None


def _split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Dimensions → group_by
# ---------------------------------------------------------------------------


def group_by_fields(query: AnalyticsQuery) -> list[str]:
    """Собрать ``group_by``: имена полей в порядке dimensions.

    Для dimension с ``time_granularity`` используется специальное имя
    ``TIME_BUCKET_COLUMN`` (``date_bucket``).
    """
    fields: list[str] = []
    for d in query.dimensions:
        fields.append(TIME_BUCKET_COLUMN if d.time_granularity is not None else d.field)
    return fields


def time_granularity_value(query: AnalyticsQuery) -> str | None:
    """Вернуть значение ``time_granularity`` первого time-dimension (или None)."""
    for d in query.dimensions:
        if d.time_granularity is not None:
            return d.time_granularity.value
    return None


def dimension_aliases(query: AnalyticsQuery) -> list[str]:
    """Алиасы колонок для dimensions в результирующем DTO.

    Если ``alias`` не задан — используется исходное имя поля.
    Для time-dimension без alias возвращается имя поля
    (``date_bucket`` остаётся «внутренним», в результате его быть не должно).
    """
    out: list[str] = []
    for d in query.dimensions:
        out.append(d.alias or d.field)
    return out


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def primary_metric_alias(query: AnalyticsQuery) -> str:
    """Алиас для основной (единственной в MVP) метрики результата."""
    if not query.metrics:
        return "count"
    m = query.metrics[0]
    return m.alias or f"{m.aggregation.value}_{m.field}"


# ---------------------------------------------------------------------------
# Sort
# ---------------------------------------------------------------------------


def sort_pairs(query: AnalyticsQuery) -> list[tuple[str, str]]:
    """Собрать ``[(field, 'asc'|'desc'), ...]`` для провайдера."""
    return [(s.field, s.order.value) for s in query.sort]


# ---------------------------------------------------------------------------
# Result assembly
# ---------------------------------------------------------------------------


def build_result(
    *,
    query: AnalyticsQuery,
    rows: list[dict[str, Any]],
    dimension_source_keys: list[str] | None = None,
    metric_source_key: str | None = None,
) -> AnalyticsResultDTO:
    """Сконвертировать строки провайдера в ``AnalyticsResultDTO``.

    Аргументы:
        rows: выход провайдера.
        dimension_source_keys: какие ключи провайдера соответствуют
            dimensions ``query`` (в том же порядке). Если ``None`` —
            берётся ``group_by_fields(query)``.
        metric_source_key: ключ провайдера, содержащий значение метрики.
            Если ``None`` — пытаемся ``"count"``.

    Имена колонок результата:
        - dimensions → их alias (или ``field``);
        - метрика → ``primary_metric_alias(query)``.
    """
    dim_keys = dimension_source_keys if dimension_source_keys is not None else group_by_fields(query)
    dim_aliases = dimension_aliases(query)
    metric_alias = primary_metric_alias(query)
    metric_key = metric_source_key or "count"

    columns: list[str] = list(dim_aliases)
    # Always include metric column: either metrics are explicitly requested,
    # or the provider was called with a metric and rows contain it.
    if query.metrics or metric_source_key is not None or rows:
        columns.append(metric_alias)

    result_rows: list[AnalyticsResultRowDTO] = []
    for row in rows:
        values: dict[str, Any] = {}
        for src_key, alias in zip(dim_keys, dim_aliases, strict=True):
            values[alias] = row.get(src_key)
        if metric_alias in columns:
            values[metric_alias] = row.get(metric_key, 0)
        result_rows.append(AnalyticsResultRowDTO(values=values))

    return AnalyticsResultDTO(
        data_source=query.data_source.value,
        bounded_context=query.bounded_context.value,
        columns=columns,
        rows=result_rows,
        total=len(result_rows),
        generated_at=iso_now(),
    )


def build_raw_result(
    *,
    query: AnalyticsQuery,
    rows: list[dict[str, Any]],
    columns: list[str],
) -> AnalyticsResultDTO:
    """Собрать ``AnalyticsResultDTO`` для «сырого» режима (raw=True).

    Используется когда у запроса нет metrics/dimensions, а провайдер
    отдаёт колонки напрямую (например, list_workspaces без group_by).
    """
    result_rows = [
        AnalyticsResultRowDTO(values={col: row.get(col) for col in columns})
        for row in rows
    ]
    return AnalyticsResultDTO(
        data_source=query.data_source.value,
        bounded_context=query.bounded_context.value,
        columns=columns,
        rows=result_rows,
        total=len(result_rows),
        generated_at=iso_now(),
    )
