from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import Select, asc, case, desc, func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.context.timetracking.application.ports.integration.outboard.timetracking_analytics_provider import (
    TimeTrackingAnalyticsProvider,
)
from app.context.timetracking.infrastructure.persistence.orm_models.time_entry_orm import (
    TimeEntryORM,
)

from app.core.logging import get_logger

_logger = get_logger(__name__)


_GROUP_FIELD_TO_COLUMN = {
    "user_id": TimeEntryORM.user_id,
    "project_id": TimeEntryORM.project_id,
    "task_id": TimeEntryORM.task_id,
    "epic_id": TimeEntryORM.epic_id,
    "category_id": TimeEntryORM.category_id,
    "status": TimeEntryORM.status,
    "is_billable": TimeEntryORM.is_billable,
}
_GRANULARITY_TO_TRUNC = {
    "hour": "hour",
    "day": "day",
    "week": "week",
    "month": "month",
    "quarter": "quarter",
    "year": "year",
}


class SqlTimeTrackingAnalyticsAdapter(TimeTrackingAnalyticsProvider):
    """SQL-реализация ``TimeTrackingAnalyticsProvider``."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def time_entry_aggregates(
        self,
        *,
        workspace_id: str,
        user_ids: list[str] | None = None,
        project_ids: list[str] | None = None,
        task_ids: list[str] | None = None,
        epic_ids: list[str] | None = None,
        category_ids: list[str] | None = None,
        is_billable: bool | None = None,
        statuses: list[str] | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        granularity: str | None = None,
        group_by: list[str] | None = None,
        metric: str = "count",
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        ws_uuid = uuid.UUID(workspace_id)
        group_by = group_by or []

        select_cols: list[Any] = []
        labels: list[str] = []
        group_exprs: list[Any] = []
        for field in group_by:
            if field == "date_bucket":
                bucket = func.date_trunc(
                    _GRANULARITY_TO_TRUNC.get((granularity or "day").lower(), "day"),
                    TimeEntryORM.entry_date,
                )
                expr = bucket.label("date_bucket")
                select_cols.append(expr)
                group_exprs.append(bucket)
                labels.append("date_bucket")
                continue
            col = _GROUP_FIELD_TO_COLUMN.get(field)
            if col is None:
                raise ValueError(f"Unsupported group_by field: {field}")
            select_cols.append(col.label(field))
            group_exprs.append(col)
            labels.append(field)

        metric_expr, metric_label = _metric_expression(metric)
        select_cols.append(metric_expr.label(metric_label))

        stmt: Select[Any] = select(*select_cols).where(
            TimeEntryORM.workspace_id == ws_uuid
        )
        stmt = _apply_filters(
            stmt,
            user_ids=user_ids,
            project_ids=project_ids,
            task_ids=task_ids,
            epic_ids=epic_ids,
            category_ids=category_ids,
            is_billable=is_billable,
            statuses=statuses,
            date_from=date_from,
            date_to=date_to,
        )
        if group_exprs:
            stmt = stmt.group_by(*group_exprs)
        stmt = _apply_sort(stmt, sort, labels=labels, metric_label=metric_label)
        if limit:
            stmt = stmt.limit(limit)

        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).all()
        out: list[dict[str, Any]] = []
        for r in rows:
            data: dict[str, Any] = {}
            for label, value in zip(labels, r[: len(labels)], strict=True):
                data[label] = _coerce(value)
            metric_value = r[len(labels)]
            data[metric_label] = _coerce_metric(metric_value, metric_label)
            out.append(data)
        return out

    async def workload_by_user(
        self,
        *,
        workspace_id: str,
        user_ids: list[str] | None = None,
        project_ids: list[str] | None = None,
        date_from: date,
        date_to: date,
        granularity: str = "day",
    ) -> list[dict[str, Any]]:
        ws_uuid = uuid.UUID(workspace_id)
        bucket = func.date_trunc(
            _GRANULARITY_TO_TRUNC.get(granularity.lower(), "day"),
            TimeEntryORM.entry_date,
        ).label("date_bucket")
        stmt: Select[Any] = (
            select(
                TimeEntryORM.user_id.label("user_id"),
                bucket,
                func.coalesce(func.sum(TimeEntryORM.duration_seconds), 0).label(
                    "total_duration_seconds"
                ),
            )
            .where(TimeEntryORM.workspace_id == ws_uuid)
            .where(TimeEntryORM.entry_date >= date_from)
            .where(TimeEntryORM.entry_date <= date_to)
        )
        if user_ids:
            stmt = stmt.where(TimeEntryORM.user_id.in_([uuid.UUID(x) for x in user_ids]))
        if project_ids:
            stmt = stmt.where(TimeEntryORM.project_id.in_([uuid.UUID(x) for x in project_ids]))
        stmt = stmt.group_by(TimeEntryORM.user_id, bucket)
        stmt = stmt.order_by(asc(TimeEntryORM.user_id), asc(bucket))

        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).all()
        return [
            {
                "user_id": _coerce(r[0]),
                "date_bucket": _coerce(r[1]),
                "total_duration_seconds": int(r[2] or 0),
            }
            for r in rows
        ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _metric_expression(metric: str):
    if metric == "count":
        return func.count(), "count"
    if metric == "sum_duration":
        return func.coalesce(func.sum(TimeEntryORM.duration_seconds), 0), "sum_duration"
    if metric == "avg_duration":
        return func.coalesce(func.avg(TimeEntryORM.duration_seconds), 0), "avg_duration"
    if metric == "sum_billable":
        # Биллингуемые секунды × ставку (если задана). В MVP — только
        # секунды биллингуемых entries, без денежной размерности.
        expr = func.coalesce(
            func.sum(
                case(
                    (TimeEntryORM.is_billable.is_(True), TimeEntryORM.duration_seconds),
                    else_=0,
                )
            ),
            0,
        )
        return expr, "sum_billable"
    raise ValueError(f"Unsupported metric: {metric}")


def _apply_filters(
    stmt: Select[Any],
    *,
    user_ids: list[str] | None,
    project_ids: list[str] | None,
    task_ids: list[str] | None,
    epic_ids: list[str] | None,
    category_ids: list[str] | None,
    is_billable: bool | None,
    statuses: list[str] | None,
    date_from: date | None,
    date_to: date | None,
) -> Select[Any]:
    if user_ids:
        stmt = stmt.where(TimeEntryORM.user_id.in_([uuid.UUID(x) for x in user_ids]))
    if project_ids:
        stmt = stmt.where(TimeEntryORM.project_id.in_([uuid.UUID(x) for x in project_ids]))
    if task_ids:
        stmt = stmt.where(TimeEntryORM.task_id.in_([uuid.UUID(x) for x in task_ids]))
    if epic_ids:
        stmt = stmt.where(TimeEntryORM.epic_id.in_([uuid.UUID(x) for x in epic_ids]))
    if category_ids:
        stmt = stmt.where(TimeEntryORM.category_id.in_([uuid.UUID(x) for x in category_ids]))
    if is_billable is not None:
        stmt = stmt.where(TimeEntryORM.is_billable.is_(is_billable))
    if statuses:
        stmt = stmt.where(TimeEntryORM.status.in_(statuses))
    if date_from:
        stmt = stmt.where(TimeEntryORM.entry_date >= date_from)
    if date_to:
        stmt = stmt.where(TimeEntryORM.entry_date <= date_to)
    return stmt


def _apply_sort(
    stmt: Select[Any],
    sort: list[tuple[str, str]] | None,
    *,
    labels: list[str],
    metric_label: str,
) -> Select[Any]:
    if not sort:
        return stmt
    for field, direction in sort:
        order = asc if direction.lower() == "asc" else desc
        if field == metric_label:
            stmt = stmt.order_by(order(literal_column(metric_label)))
        elif field in labels:
            if field == "date_bucket":
                stmt = stmt.order_by(order(literal_column("date_bucket")))
            else:
                col = _GROUP_FIELD_TO_COLUMN.get(field)
                if col is not None:
                    stmt = stmt.order_by(order(col))
                else:
                    _logger.warning("Unknown sort field ignored", field=field)
    return stmt


def _coerce(value: Any) -> Any:
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def _coerce_metric(value: Any, metric_label: str) -> Any:
    if value is None:
        return 0
    if metric_label in ("count", "sum_duration", "sum_billable"):
        return int(value)
    if metric_label == "avg_duration":
        return float(value)
    return value
