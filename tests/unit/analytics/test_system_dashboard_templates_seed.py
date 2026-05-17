"""Unit-тесты для seed-данных системных шаблонов дашбордов.

Проверяет, что все JSON-payload'ы виджетов валидно десериализуются в
доменные ``WidgetConfig``/``AnalyticsQuery`` через тот же путь, что
используется при чтении из БД (``widget_config_from_json``).
"""
from __future__ import annotations

import pytest

from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.domain.value_objects.widget_type import WidgetType
from app.context.analytics.infrastructure.persistence.mappers._query_serialization import (
    widget_config_from_json,
)
from app.context.analytics.infrastructure.persistence.seed.system_dashboard_templates import (
    SYSTEM_DASHBOARD_TEMPLATES,
)
from tests.unit.analytics.conftest import RESOLVER_SUPPORTED_DATA_SOURCES

pytestmark = pytest.mark.unit


def test_system_templates_are_not_empty() -> None:
    assert len(SYSTEM_DASHBOARD_TEMPLATES) >= 3


def test_system_templates_have_unique_ids() -> None:
    ids = [t["id"] for t in SYSTEM_DASHBOARD_TEMPLATES]
    assert len(ids) == len(set(ids)), "Дубликаты UUID в SYSTEM_DASHBOARD_TEMPLATES"


def test_system_templates_have_unique_names() -> None:
    names = [t["name"] for t in SYSTEM_DASHBOARD_TEMPLATES]
    assert len(names) == len(set(names)), "Дубликаты имён в SYSTEM_DASHBOARD_TEMPLATES"


@pytest.mark.parametrize("template", SYSTEM_DASHBOARD_TEMPLATES, ids=lambda t: t["name"])
def test_template_invariants(template: dict) -> None:
    """Системные шаблоны должны быть глобальными (workspace_id is None, is_system=True)."""
    assert template["is_system"] is True
    assert template["workspace_id"] is None
    assert template["is_deleted"] is False
    assert template["name"]
    assert isinstance(template["widget_configs"], list)
    assert len(template["widget_configs"]) > 0


@pytest.mark.parametrize("template", SYSTEM_DASHBOARD_TEMPLATES, ids=lambda t: t["name"])
def test_template_widgets_deserialize(template: dict) -> None:
    """Каждый widget_config валидно десериализуется в WidgetConfig.

    Это гарантирует, что ``DashboardTemplateMapper.to_domain`` не уронит
    шаблон при чтении из БД.
    """
    for cfg in template["widget_configs"]:
        widget = widget_config_from_json(cfg)
        assert isinstance(widget, WidgetConfig)
        # widget_type — валидный enum.
        assert isinstance(widget.widget_type, WidgetType)
        # data_source — валидный enum.
        assert isinstance(widget.query.data_source, DataSource)


@pytest.mark.parametrize("template", SYSTEM_DASHBOARD_TEMPLATES, ids=lambda t: t["name"])
def test_template_widgets_use_supported_data_sources(template: dict) -> None:
    """Все DataSource из системных шаблонов должны иметь зарегистрированный resolver.

    Иначе при попытке выполнить виджет через ``POST /analytics/execute``
    клиент получит ``UnsupportedDataSourceException``.
    """
    supported = RESOLVER_SUPPORTED_DATA_SOURCES
    for cfg in template["widget_configs"]:
        widget = widget_config_from_json(cfg)
        assert widget is not None
        assert widget.query.data_source in supported, (
            f"DataSource {widget.query.data_source} в шаблоне "
            f"'{template['name']}' не поддерживается ни одним resolver'ом"
        )
