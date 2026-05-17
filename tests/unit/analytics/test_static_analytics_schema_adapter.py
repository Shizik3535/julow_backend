"""Unit-тесты для ``StaticAnalyticsSchemaAdapter``.

Проверяет, что:
    - все объявленные ``DataSource`` существуют в доменном enum;
    - все агрегации/операторы/гранулярности — валидные значения enum'ов;
    - реестр покрывает только источники, реально поддержанные
      резолверами (расхождения = багу при чтении API).
"""
from __future__ import annotations

import pytest

from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.domain.value_objects.filter_operator import FilterOperator
from app.context.analytics.domain.value_objects.metric_aggregation import (
    MetricAggregation,
)
from app.context.analytics.domain.value_objects.sort_order import SortOrder
from app.context.analytics.domain.value_objects.time_granularity import TimeGranularity
from app.context.analytics.domain.value_objects.widget_type import WidgetType
from app.context.analytics.infrastructure.schema.static_analytics_schema_adapter import (
    _DATA_SOURCE_SCHEMAS,
    StaticAnalyticsSchemaAdapter,
)
from tests.unit.analytics.conftest import RESOLVER_SUPPORTED_DATA_SOURCES

pytestmark = pytest.mark.unit


def test_registry_only_contains_supported_data_sources() -> None:
    """Реестр не должен анонсировать клиенту источники без резолвера."""
    declared = set(_DATA_SOURCE_SCHEMAS.keys())
    assert declared <= RESOLVER_SUPPORTED_DATA_SOURCES, (
        f"Реестр содержит DataSource без резолвера: {declared - RESOLVER_SUPPORTED_DATA_SOURCES}"
    )


def test_registry_covers_all_supported_data_sources() -> None:
    """Все реально поддержанные DataSource должны быть в реестре."""
    declared = set(_DATA_SOURCE_SCHEMAS.keys())
    missing = RESOLVER_SUPPORTED_DATA_SOURCES - declared
    assert not missing, f"В реестре нет схемы для: {missing}"


@pytest.mark.parametrize("ds, schema", list(_DATA_SOURCE_SCHEMAS.items()), ids=lambda x: getattr(x, "name", str(x)))
def test_schema_aggregations_are_valid_enum(ds: DataSource, schema) -> None:
    valid = {a.value for a in MetricAggregation}
    for agg in schema.supported_aggregations:
        assert agg in valid, (
            f"DataSource {ds}: невалидная агрегация '{agg}'"
        )


@pytest.mark.parametrize("ds, schema", list(_DATA_SOURCE_SCHEMAS.items()), ids=lambda x: getattr(x, "name", str(x)))
def test_schema_default_metric_aggregations_are_valid(ds: DataSource, schema) -> None:
    valid = {a.value for a in MetricAggregation}
    for m in schema.default_metrics:
        assert m.aggregation in valid


def test_get_full_schema_includes_all_enums() -> None:
    adapter = StaticAnalyticsSchemaAdapter()
    payload = adapter.get_full_schema()

    assert set(payload.filter_operators) == {op.value for op in FilterOperator}
    assert set(payload.aggregations) == {a.value for a in MetricAggregation}
    assert set(payload.time_granularities) == {g.value for g in TimeGranularity}
    assert set(payload.sort_orders) == {o.value for o in SortOrder}
    assert set(payload.widget_types) == {w.value for w in WidgetType}

    declared = {s.data_source for s in payload.data_sources}
    assert declared == {ds.value for ds in _DATA_SOURCE_SCHEMAS}


def test_list_data_sources_has_one_entry_per_schema() -> None:
    adapter = StaticAnalyticsSchemaAdapter()
    items = adapter.list_data_sources()
    assert len(items) == len(_DATA_SOURCE_SCHEMAS)
    assert {i.data_source for i in items} == {ds.value for ds in _DATA_SOURCE_SCHEMAS}


def test_get_data_source_schema_known() -> None:
    adapter = StaticAnalyticsSchemaAdapter()
    schema = adapter.get_data_source_schema(DataSource.TASKS.value)
    assert schema is not None
    assert schema.data_source == DataSource.TASKS.value
    assert any(f.name == "project_id" for f in schema.fields)


def test_get_data_source_schema_unknown_returns_none() -> None:
    adapter = StaticAnalyticsSchemaAdapter()
    assert adapter.get_data_source_schema("not_a_real_data_source") is None


def test_get_data_source_schema_unsupported_returns_none() -> None:
    """Существующий в enum DataSource, но не зарегистрированный в реестре."""
    adapter = StaticAnalyticsSchemaAdapter()
    # COMMENTS / FILES / etc. — есть в enum, но резолвера нет.
    assert adapter.get_data_source_schema(DataSource.COMMENTS.value) is None
