"""Helper-маппинги доменных объектов Analytics BC в DTO и обратно."""
from __future__ import annotations

from app.context.analytics.application.dto.analytics_query_dto import (
    AnalyticsQueryDTO,
    DateRangeDTO,
    DimensionDTO,
    FilterConfigDTO,
    MetricDefinitionDTO,
    SortConfigDTO,
)
from app.context.analytics.application.dto.dashboard_dto import (
    DashboardDTO,
    DashboardShareDTO,
    WidgetDTO,
)
from app.context.analytics.application.dto.dashboard_template_dto import DashboardTemplateDTO
from app.context.analytics.application.dto.report_dto import (
    ReportDTO,
    ReportScheduleDTO,
    ReportShareDTO,
)
from app.context.analytics.domain.aggregates.dashboard import Dashboard
from app.context.analytics.domain.aggregates.dashboard_template import DashboardTemplate
from app.context.analytics.domain.aggregates.report import Report
from app.context.analytics.domain.entities.dashboard_share import DashboardShare
from app.context.analytics.domain.entities.report_schedule import ReportSchedule
from app.context.analytics.domain.entities.report_share import ReportShare
from app.context.analytics.domain.entities.widget import Widget
from app.context.analytics.domain.value_objects.analytics_query import AnalyticsQuery
from app.context.analytics.domain.value_objects.data_source import DataSource
from app.context.analytics.domain.value_objects.dimension import Dimension
from app.context.analytics.domain.value_objects.filter_config import FilterConfig
from app.context.analytics.domain.value_objects.filter_operator import FilterOperator
from app.context.analytics.domain.value_objects.metric_aggregation import MetricAggregation
from app.context.analytics.domain.value_objects.metric_definition import MetricDefinition
from app.context.analytics.domain.value_objects.sort_config import SortConfig
from app.context.analytics.domain.value_objects.sort_order import SortOrder
from app.context.analytics.domain.value_objects.time_granularity import TimeGranularity
from app.context.analytics.domain.value_objects.widget_config import WidgetConfig
from app.context.analytics.domain.value_objects.widget_position import WidgetPosition
from app.context.analytics.domain.value_objects.widget_size import WidgetSize
from app.context.analytics.domain.value_objects.widget_type import WidgetType
from app.shared.domain.exceptions import ValidationException
from app.shared.domain.value_objects.date_range_vo import DateRange


# ---------- AnalyticsQuery <-> DTO ----------

def analytics_query_to_dto(query: AnalyticsQuery) -> AnalyticsQueryDTO:
    return AnalyticsQueryDTO(
        data_source=query.data_source.value,
        metrics=[
            MetricDefinitionDTO(
                field=m.field, aggregation=m.aggregation.value, alias=m.alias
            )
            for m in query.metrics
        ],
        dimensions=[
            DimensionDTO(
                field=d.field,
                time_granularity=d.time_granularity.value if d.time_granularity else None,
                alias=d.alias,
            )
            for d in query.dimensions
        ],
        filters=[
            FilterConfigDTO(
                field=f.field, operator=f.operator.value, value=f.value, value_to=f.value_to
            )
            for f in query.filters
        ],
        date_range=(
            DateRangeDTO(start=query.date_range.start, end=query.date_range.end)
            if query.date_range is not None
            else None
        ),
        sort=[SortConfigDTO(field=s.field, order=s.order.value) for s in query.sort],
        limit=query.limit,
        raw=query.raw,
    )


def analytics_query_from_dto(dto: AnalyticsQueryDTO) -> AnalyticsQuery:
    date_range: DateRange | None = None
    if dto.date_range is not None and (dto.date_range.start is not None or dto.date_range.end is not None):
        if dto.date_range.start is None or dto.date_range.end is None:
            # Shared DateRange требует обе границы. Полу-заданный диапазон
            # — почти всегда ошибка клиента: лучше явно отклонить, чем
            # молча терять фильтр.
            raise ValidationException(
                field="date_range",
                message="date_range требует и start, и end (или оба None)",
            )
        date_range = DateRange(start=dto.date_range.start, end=dto.date_range.end)
    return AnalyticsQuery(
        data_source=DataSource(dto.data_source),
        metrics=[
            MetricDefinition(
                field=m.field,
                aggregation=MetricAggregation(m.aggregation),
                alias=m.alias,
            )
            for m in dto.metrics
        ],
        dimensions=[
            Dimension(
                field=d.field,
                time_granularity=(
                    TimeGranularity(d.time_granularity) if d.time_granularity else None
                ),
                alias=d.alias,
            )
            for d in dto.dimensions
        ],
        filters=[
            FilterConfig(
                field=f.field,
                operator=FilterOperator(f.operator),
                value=f.value,
                value_to=f.value_to,
            )
            for f in dto.filters
        ],
        date_range=date_range,
        sort=[SortConfig(field=s.field, order=SortOrder(s.order)) for s in dto.sort],
        limit=dto.limit,
        raw=dto.raw,
    )


# ---------- Widget ----------

def widget_to_dto(widget: Widget) -> WidgetDTO:
    return WidgetDTO(
        id=str(widget.id),
        title=widget.title,
        widget_type=widget.widget_type.value,
        order=widget.order,
        size={"cols": widget.size.cols, "rows": widget.size.rows},
        position=(
            {"row": widget.position.row, "col": widget.position.col}
            if widget.position is not None
            else None
        ),
        query=(
            analytics_query_to_dto(widget.config.query)
            if widget.config is not None
            else None
        ),
        display_params=(widget.config.display_params if widget.config is not None else {}),
    )


def widget_config_from_dto(
    widget_type: WidgetType,
    query_dto: AnalyticsQueryDTO,
    display_params: dict | None = None,
) -> WidgetConfig:
    return WidgetConfig(
        widget_type=widget_type,
        query=analytics_query_from_dto(query_dto),
        display_params=display_params or {},
    )


def widget_size_from_dict(d: dict | None) -> WidgetSize:
    """Полный конструктор: используется для создания, отсутствие ключей даёт дефолты."""
    if not d:
        return WidgetSize()
    return WidgetSize(cols=int(d.get("cols", 6)), rows=int(d.get("rows", 4)))


def widget_position_from_dict(d: dict | None) -> WidgetPosition | None:
    """Полный конструктор: пустой dict / None → нет позиции."""
    if not d:
        return None
    return WidgetPosition(row=int(d.get("row", 0)), col=int(d.get("col", 0)))


def widget_size_merge(current: WidgetSize, patch: dict | None) -> WidgetSize | None:
    """Частичное обновление: мерджим только присутствующие в patch ключи.

    Возвращает None, если patch пустой/None (значит, обновлять нечего).
    """
    if not patch:
        return None
    cols = int(patch["cols"]) if "cols" in patch else current.cols
    rows = int(patch["rows"]) if "rows" in patch else current.rows
    return WidgetSize(cols=cols, rows=rows)


def widget_position_merge(
    current: WidgetPosition | None, patch: dict | None
) -> WidgetPosition | None:
    """Частичное обновление позиции с сохранением неуказанных координат."""
    if not patch:
        return None
    base_row = current.row if current is not None else 0
    base_col = current.col if current is not None else 0
    row = int(patch["row"]) if "row" in patch else base_row
    col = int(patch["col"]) if "col" in patch else base_col
    return WidgetPosition(row=row, col=col)


# ---------- Dashboard ----------

def dashboard_share_to_dto(share: DashboardShare) -> DashboardShareDTO:
    return DashboardShareDTO(
        user_id=str(share.user_id),
        access_level=share.access_level.value,
        shared_at=share.shared_at,
    )


def dashboard_to_dto(dashboard: Dashboard) -> DashboardDTO:
    return DashboardDTO(
        id=str(dashboard.id),
        owner_id=str(dashboard.owner_id),
        workspace_id=str(dashboard.workspace_id) if dashboard.workspace_id else None,
        name=dashboard.name,
        description=dashboard.description,
        widgets=[widget_to_dto(w) for w in dashboard.widgets],
        shares=[dashboard_share_to_dto(s) for s in dashboard.shares],
        is_auto_refresh=dashboard.is_auto_refresh,
        refresh_interval_seconds=dashboard.refresh_interval_seconds,
        is_default=dashboard.is_default,
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at,
    )


# ---------- Report ----------

def report_schedule_to_dto(schedule: ReportSchedule) -> ReportScheduleDTO:
    return ReportScheduleDTO(
        frequency=schedule.frequency.value,
        recipients=[str(r) for r in schedule.recipients],
        is_active=schedule.is_active,
        next_run_at=schedule.next_run_at,
        last_run_at=schedule.last_run_at,
    )


def report_share_to_dto(share: ReportShare) -> ReportShareDTO:
    return ReportShareDTO(
        user_id=str(share.user_id),
        access_level=share.access_level.value,
        shared_at=share.shared_at,
    )


def report_to_dto(report: Report) -> ReportDTO:
    return ReportDTO(
        id=str(report.id),
        owner_id=str(report.owner_id),
        workspace_id=str(report.workspace_id) if report.workspace_id else None,
        name=report.name,
        description=report.description,
        report_type=report.report_type.value,
        query=analytics_query_to_dto(report.query),
        schedule=report_schedule_to_dto(report.schedule) if report.schedule else None,
        shares=[report_share_to_dto(s) for s in report.shares],
        last_generated_at=report.last_generated_at,
        last_export_format=(
            report.last_export_format.value if report.last_export_format else None
        ),
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


# ---------- DashboardTemplate ----------

def dashboard_template_to_dto(template: DashboardTemplate) -> DashboardTemplateDTO:
    # Шаблоны хранят widget_configs (без позиций/размеров) — рендерим как WidgetDTO с дефолтами.
    widgets: list[WidgetDTO] = []
    for i, cfg in enumerate(template.widget_configs):
        widgets.append(
            WidgetDTO(
                id="",
                title=cfg.widget_type.value,
                widget_type=cfg.widget_type.value,
                order=i,
                size={"cols": 6, "rows": 4},
                position=None,
                query=analytics_query_to_dto(cfg.query),
                display_params=cfg.display_params,
            )
        )
    return DashboardTemplateDTO(
        id=str(template.id),
        name=template.name,
        description=template.description,
        widgets=widgets,
        is_system=template.is_system,
        created_at=template.created_at,
        updated_at=template.updated_at,
    )
