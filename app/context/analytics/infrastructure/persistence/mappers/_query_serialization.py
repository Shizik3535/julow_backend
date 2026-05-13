"""Сериализация ``AnalyticsQuery`` / ``WidgetConfig`` для хранения в JSONB.

Использует существующие DTO-мэпперы application-слоя: они уже покрывают
полную трансляцию доменных VO в плоскую структуру и обратно, дублировать
маппинг на инфраструктурном слое нет смысла.
"""
from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.context.analytics.application.dto.analytics_query_dto import AnalyticsQueryDTO
from app.context.analytics.application.dto.mappers import (
    analytics_query_from_dto,
    analytics_query_to_dto,
)
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.domain.value_objects.widget_type import WidgetType

logger = get_logger(__name__)


def analytics_query_to_json(query: AnalyticsQuery) -> dict[str, Any]:
    """Сериализовать ``AnalyticsQuery`` в JSON-совместимый dict."""
    dto = analytics_query_to_dto(query)
    return dto.model_dump(mode="json")


def analytics_query_from_json(data: dict[str, Any] | None) -> AnalyticsQuery:
    """Десериализовать ``AnalyticsQuery`` из dict.

    ``None`` (поле отсутствует в источнике) трактуем как «raw-запрос» —
    это безопасный default для виджетов/отчётов, созданных без `query`.
    Пустой dict (``{}``) НЕ считается валидным: он почти всегда означает
    повреждение данных и/или баг сериализации, и молчаливый ремаппинг в
    ``raw=True`` затирал бы реальный ``data_source`` / ``bounded_context``
    в индексных колонках. Логируем и всё равно возвращаем raw, чтобы
    обращение к старому виджету не уронило весь дашборд.
    """
    if data is None:
        return AnalyticsQuery(raw=True)
    if not data:
        logger.warning(
            "AnalyticsQuery JSON payload is empty; falling back to raw=True",
            payload=data,
        )
        return AnalyticsQuery(raw=True)
    dto = AnalyticsQueryDTO.model_validate(data)
    return analytics_query_from_dto(dto)


def widget_config_to_json(config: WidgetConfig | None) -> dict[str, Any] | None:
    """Сериализовать ``WidgetConfig`` в JSON-совместимый dict."""
    if config is None:
        return None
    return {
        "widget_type": config.widget_type.value,
        "query": analytics_query_to_json(config.query),
        "display_params": dict(config.display_params),
    }


def widget_config_from_json(data: dict[str, Any] | None) -> WidgetConfig | None:
    """Десериализовать ``WidgetConfig`` из dict.

    ``None``/отсутствие столбца — легитимный случай (виджет без config).
    Пустой dict — повреждение данных: предупреждаем и возвращаем ``None``,
    чтобы вышестоящий маппер мог решить, дропать виджет или нет.
    """
    if data is None:
        return None
    if not data:
        logger.warning(
            "WidgetConfig JSON payload is empty; treating as missing",
            payload=data,
        )
        return None
    if "widget_type" not in data:
        logger.warning(
            "WidgetConfig JSON payload is missing widget_type; treating as missing",
            payload=data,
        )
        return None
    widget_type = WidgetType(data["widget_type"])
    query = analytics_query_from_json(data.get("query"))
    display_params = data.get("display_params") or {}
    return WidgetConfig(
        widget_type=widget_type,
        query=query,
        display_params=dict(display_params),
    )
