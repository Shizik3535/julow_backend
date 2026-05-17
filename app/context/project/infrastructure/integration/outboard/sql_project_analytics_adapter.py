from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.logging import get_logger
from app.context.project.application.ports.integration.outboard.project_analytics_provider import (
    ProjectAnalyticsProvider,
)
from app.context.project.infrastructure.persistence.orm_models.project_orm import ProjectORM

_logger = get_logger(__name__)


_SUPPORTED_GROUP_FIELDS = {
    "status",
    "visibility",
    "methodology",
    "category_name",
    "workspace_id",
}
_DATE_FIELDS = {
    "created_at": ProjectORM.created_at,
    "start_date": ProjectORM.start_date,
    "deadline": ProjectORM.deadline,
}
_GRANULARITY_TO_TRUNC = {
    "hour": "hour",
    "day": "day",
    "week": "week",
    "month": "month",
    "quarter": "quarter",
    "year": "year",
}


class SqlProjectAnalyticsAdapter(ProjectAnalyticsProvider):
    """SQL-реализация ``ProjectAnalyticsProvider``."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_projects(
        self,
        *,
        workspace_id: str,
        project_ids: list[str] | None = None,
        statuses: list[str] | None = None,
        visibilities: list[str] | None = None,
        methodologies: list[str] | None = None,
        date_field: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        granularity: str | None = None,
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        ws_uuid = uuid.UUID(workspace_id)
        if group_by:
            return await self._aggregate(
                workspace_id=ws_uuid,
                project_ids=project_ids,
                statuses=statuses,
                visibilities=visibilities,
                methodologies=methodologies,
                date_field=date_field,
                date_from=date_from,
                date_to=date_to,
                granularity=granularity,
                group_by=group_by,
                sort=sort,
                limit=limit,
            )
        return await self._list_rows(
            workspace_id=ws_uuid,
            project_ids=project_ids,
            statuses=statuses,
            visibilities=visibilities,
            methodologies=methodologies,
            date_field=date_field,
            date_from=date_from,
            date_to=date_to,
            sort=sort,
            limit=limit,
        )

    async def project_summaries(
        self,
        *,
        workspace_id: str,
        project_ids: list[str] | None = None,
        statuses: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        ws_uuid = uuid.UUID(workspace_id)
        stmt: Select[Any] = select(
            ProjectORM.id,
            ProjectORM.name,
            ProjectORM.status,
            ProjectORM.start_date,
            ProjectORM.deadline,
            ProjectORM.methodology,
        ).where(ProjectORM.workspace_id == ws_uuid)
        if project_ids:
            stmt = stmt.where(ProjectORM.id.in_([uuid.UUID(x) for x in project_ids]))
        if statuses:
            stmt = stmt.where(ProjectORM.status.in_(statuses))
        if limit:
            stmt = stmt.limit(limit)

        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).mappings().all()
        return [
            {
                "project_id": str(r["id"]),
                "name": r["name"],
                "status": r["status"],
                "start_date": r["start_date"],
                "deadline": r["deadline"],
                "methodology": r["methodology"],
            }
            for r in rows
        ]

    # ------------------------------------------------------------------

    async def _list_rows(
        self,
        *,
        workspace_id: uuid.UUID,
        project_ids: list[str] | None,
        statuses: list[str] | None,
        visibilities: list[str] | None,
        methodologies: list[str] | None,
        date_field: str | None,
        date_from: date | None,
        date_to: date | None,
        sort: list[tuple[str, str]] | None,
        limit: int | None,
    ) -> list[dict[str, Any]]:
        stmt: Select[Any] = select(
            ProjectORM.id,
            ProjectORM.name,
            ProjectORM.status,
            ProjectORM.visibility,
            ProjectORM.methodology,
            ProjectORM.start_date,
            ProjectORM.deadline,
            ProjectORM.created_at,
            ProjectORM.workspace_id,
        ).where(ProjectORM.workspace_id == workspace_id)
        stmt = _apply_common_filters(
            stmt,
            project_ids=project_ids,
            statuses=statuses,
            visibilities=visibilities,
            methodologies=methodologies,
            date_field=date_field,
            date_from=date_from,
            date_to=date_to,
        )
        stmt = _apply_sort(stmt, sort, group_columns=None)
        if limit:
            stmt = stmt.limit(limit)
        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).mappings().all()
        return [
            {
                "id": str(r["id"]),
                "name": r["name"],
                "status": r["status"],
                "visibility": r["visibility"],
                "methodology": r["methodology"],
                "start_date": r["start_date"],
                "deadline": r["deadline"],
                "created_at": r["created_at"],
                "workspace_id": str(r["workspace_id"]) if r["workspace_id"] else None,
            }
            for r in rows
        ]

    async def _aggregate(
        self,
        *,
        workspace_id: uuid.UUID,
        project_ids: list[str] | None,
        statuses: list[str] | None,
        visibilities: list[str] | None,
        methodologies: list[str] | None,
        date_field: str | None,
        date_from: date | None,
        date_to: date | None,
        granularity: str | None,
        group_by: list[str],
        sort: list[tuple[str, str]] | None,
        limit: int | None,
    ) -> list[dict[str, Any]]:
        select_cols: list[Any] = []
        labels: list[str] = []
        for field in group_by:
            if field == "date_bucket":
                col_expr, label = _date_bucket_expr(date_field, granularity)
                select_cols.append(col_expr)
                labels.append(label)
                continue
            if field not in _SUPPORTED_GROUP_FIELDS:
                raise ValueError(f"Unsupported group_by field: {field}")
            col = _column_for(field)
            select_cols.append(col.label(field))
            labels.append(field)

        count_col = func.count().label("count")
        stmt: Select[Any] = select(*select_cols, count_col).where(
            ProjectORM.workspace_id == workspace_id
        )
        stmt = _apply_common_filters(
            stmt,
            project_ids=project_ids,
            statuses=statuses,
            visibilities=visibilities,
            methodologies=methodologies,
            date_field=date_field,
            date_from=date_from,
            date_to=date_to,
        )
        stmt = stmt.group_by(*select_cols)
        stmt = _apply_sort(
            stmt,
            sort,
            group_columns={label: col for label, col in zip(labels, select_cols, strict=True)},
        )
        if limit:
            stmt = stmt.limit(limit)
        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).all()
        out: list[dict[str, Any]] = []
        for r in rows:
            data: dict[str, Any] = {}
            for label, value in zip(labels, r[:-1], strict=True):
                data[label] = _coerce(value)
            data["count"] = int(r[-1])
            out.append(data)
        return out


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _column_for(field: str):
    if field == "status":
        return ProjectORM.status
    if field == "visibility":
        return ProjectORM.visibility
    if field == "methodology":
        return ProjectORM.methodology
    if field == "category_name":
        return ProjectORM.category_name
    if field == "workspace_id":
        return ProjectORM.workspace_id
    raise ValueError(f"Unsupported group field: {field}")


def _date_bucket_expr(date_field: str | None, granularity: str | None):
    column = _DATE_FIELDS.get(date_field or "created_at")
    if column is None:
        raise ValueError(f"Unsupported date_field: {date_field}")
    trunc = _GRANULARITY_TO_TRUNC.get((granularity or "day").lower(), "day")
    return func.date_trunc(trunc, column).label("date_bucket"), "date_bucket"


def _apply_common_filters(
    stmt: Select[Any],
    *,
    project_ids: list[str] | None,
    statuses: list[str] | None,
    visibilities: list[str] | None,
    methodologies: list[str] | None,
    date_field: str | None,
    date_from: date | None,
    date_to: date | None,
) -> Select[Any]:
    if project_ids:
        stmt = stmt.where(ProjectORM.id.in_([uuid.UUID(x) for x in project_ids]))
    if statuses:
        stmt = stmt.where(ProjectORM.status.in_(statuses))
    if visibilities:
        stmt = stmt.where(ProjectORM.visibility.in_(visibilities))
    if methodologies:
        stmt = stmt.where(ProjectORM.methodology.in_(methodologies))
    if date_field and (date_from or date_to):
        column = _DATE_FIELDS.get(date_field)
        if column is not None:
            if date_from:
                stmt = stmt.where(column >= date_from)
            if date_to:
                stmt = stmt.where(column <= date_to)
    return stmt


def _apply_sort(
    stmt: Select[Any],
    sort: list[tuple[str, str]] | None,
    *,
    group_columns: dict[str, Any] | None,
) -> Select[Any]:
    if not sort:
        return stmt
    for field, direction in sort:
        order = asc if direction.lower() == "asc" else desc
        if group_columns and field in group_columns:
            stmt = stmt.order_by(order(group_columns[field]))
        elif field == "count":
            if group_columns is None:
                _logger.warning("Sort by 'count' ignored in non-aggregate mode", field=field)
            else:
                stmt = stmt.order_by(order(func.count()))
        elif group_columns is None:
            col = getattr(ProjectORM, field, None)
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
