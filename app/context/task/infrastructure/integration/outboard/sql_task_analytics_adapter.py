from __future__ import annotations

import json
import uuid
from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy import (
    Select,
    asc,
    case,
    cast,
    desc,
    func,
    literal_column,
    or_,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.context.task.application.ports.integration.outboard.task_analytics_provider import (
    TaskAnalyticsProvider,
)
from app.context.task.infrastructure.persistence.orm_models.task_orm import TaskORM

from app.core.logging import get_logger

# Sprint ORM физически живёт в Project BC. Task BC's analytics-адаптер
# вынужден читать её, потому что `DataSource.SPRINTS`/`SPRINT_BURNDOWN`/
# `SPRINT_VELOCITY` по spec принадлежат Task BC, но sprint metadata
# (start/end) лежит в Project BC. Это единственная допустимая «утечка»
# — она ограничена analytics-путём и не используется в use case'ах.
from app.context.project.infrastructure.persistence.orm_models.project_orm import ProjectORM
from app.context.project.infrastructure.persistence.orm_models.sprint_orm import SprintORM

_logger = get_logger(__name__)


_GROUP_FIELD_TO_COLUMN = {
    "status_id": TaskORM.status_id,
    "priority": TaskORM.priority,
    "task_type": TaskORM.task_type,
    "status": TaskORM.status,
    "project_id": TaskORM.project_id,
    "sprint_id": TaskORM.sprint_id,
    "epic_id": TaskORM.epic_id,
}
_SPRINT_GROUP_FIELD_TO_COLUMN = {
    "status": SprintORM.status,
    "project_id": SprintORM.project_id,
}
_DATE_FIELDS = {
    "created_at": TaskORM.created_at,
    "completed_at": TaskORM.completed_at,
    "due_date": TaskORM.due_date,
    "start_date": TaskORM.start_date,
}
_GRANULARITY_TO_TRUNC = {
    "hour": "hour",
    "day": "day",
    "week": "week",
    "month": "month",
    "quarter": "quarter",
    "year": "year",
}


class SqlTaskAnalyticsAdapter(TaskAnalyticsProvider):
    """SQL-реализация ``TaskAnalyticsProvider``."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    # ------------------------------------------------------------------
    # count_tasks
    # ------------------------------------------------------------------

    async def count_tasks(
        self,
        *,
        workspace_id: str,
        project_ids: list[str] | None = None,
        sprint_ids: list[str] | None = None,
        epic_ids: list[str] | None = None,
        assignee_ids: list[str] | None = None,
        status_ids: list[str] | None = None,
        priorities: list[str] | None = None,
        task_types: list[str] | None = None,
        statuses: list[str] | None = None,
        completed: bool | None = None,
        date_field: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        granularity: str | None = None,
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        group_by = group_by or []
        select_cols: list[Any] = []
        labels: list[str] = []
        group_exprs: list[Any] = []
        for field in group_by:
            if field == "date_bucket":
                col = _DATE_FIELDS.get(date_field or "created_at")
                if col is None:
                    raise ValueError(f"Unsupported date_field: {date_field}")
                trunc = _GRANULARITY_TO_TRUNC.get((granularity or "day").lower(), "day")
                bucket = func.date_trunc(trunc, col)
                select_cols.append(bucket.label("date_bucket"))
                group_exprs.append(bucket)
                labels.append("date_bucket")
                continue
            if field == "assignee_id":
                # assignee_ids — JSONB-массив; группировка через jsonb_array_elements_text.
                # MVP: пропускаем эту группировку (требует cross-product unnesting).
                raise ValueError(
                    "group_by=assignee_id пока не поддерживается (требует unnest JSONB)"
                )
            col = _GROUP_FIELD_TO_COLUMN.get(field)
            if col is None:
                raise ValueError(f"Unsupported group_by field: {field}")
            select_cols.append(col.label(field))
            group_exprs.append(col)
            labels.append(field)

        select_cols.append(func.count().label("count"))

        # Anchor FROM TaskORM explicitly — needed when neither group_by nor
        # filters reference TaskORM columns (e.g. plain count with workspace
        # filter only); otherwise SQLAlchemy cannot infer the FROM clause.
        stmt: Select[Any] = (
            select(*select_cols)
            .select_from(TaskORM)
            .join(ProjectORM, TaskORM.project_id == ProjectORM.id)
        )
        # Всегда фильтруем по workspace через join с ProjectORM,
        # даже если project_ids заданы — гарантируем изоляцию workspace.
        ws_uuid = uuid.UUID(workspace_id)
        stmt = stmt.where(ProjectORM.workspace_id == ws_uuid)
        stmt = _apply_count_filters(
            stmt,
            project_ids=project_ids,
            sprint_ids=sprint_ids,
            epic_ids=epic_ids,
            assignee_ids=assignee_ids,
            status_ids=status_ids,
            priorities=priorities,
            task_types=task_types,
            statuses=statuses,
            completed=completed,
            date_field=date_field,
            date_from=date_from,
            date_to=date_to,
        )
        if group_exprs:
            stmt = stmt.group_by(*group_exprs)
        stmt = _apply_sort(stmt, sort, labels=labels, metric_label="count")
        if limit:
            stmt = stmt.limit(limit)

        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).all()
        if not labels:
            # Без group_by — одна строка с count.
            count = int(rows[0][0]) if rows else 0
            return [{"count": count}]
        out: list[dict[str, Any]] = []
        for r in rows:
            data: dict[str, Any] = {}
            for label, value in zip(labels, r[: len(labels)], strict=True):
                data[label] = _coerce(value)
            data["count"] = int(r[len(labels)] or 0)
            out.append(data)
        return out

    # ------------------------------------------------------------------
    # list_sprints
    # ------------------------------------------------------------------

    async def list_sprints(
        self,
        *,
        project_ids: list[str],
        sprint_ids: list[str] | None = None,
        statuses: list[str] | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        project_uuids = [uuid.UUID(x) for x in project_ids]

        if group_by:
            select_cols: list[Any] = []
            group_exprs: list[Any] = []
            labels: list[str] = []
            for field in group_by:
                if field == "status":
                    select_cols.append(SprintORM.status.label("status"))
                    group_exprs.append(SprintORM.status)
                    labels.append("status")
                elif field == "project_id":
                    select_cols.append(SprintORM.project_id.label("project_id"))
                    group_exprs.append(SprintORM.project_id)
                    labels.append("project_id")
                else:
                    raise ValueError(f"Unsupported group_by field for sprints: {field}")
            select_cols.append(func.count().label("count"))
            stmt: Select[Any] = (
                select(*select_cols)
                .where(SprintORM.project_id.in_(project_uuids))
                .group_by(*group_exprs)
            )
            if sprint_ids:
                stmt = stmt.where(SprintORM.id.in_([uuid.UUID(x) for x in sprint_ids]))
            if statuses:
                stmt = stmt.where(SprintORM.status.in_(statuses))
            if date_from:
                stmt = stmt.where(SprintORM.sprint_end >= date_from)
            if date_to:
                stmt = stmt.where(SprintORM.sprint_start <= date_to)
            stmt = _apply_sort(stmt, sort, labels=labels, metric_label="count", model=SprintORM)
            if limit:
                stmt = stmt.limit(limit)
            async with self._session_factory() as session:
                rows = (await session.execute(stmt)).all()
            out: list[dict[str, Any]] = []
            for r in rows:
                data: dict[str, Any] = {}
                for label, value in zip(labels, r[: len(labels)], strict=True):
                    data[label] = _coerce(value)
                data["count"] = int(r[len(labels)] or 0)
                out.append(data)
            return out

        stmt = select(
            SprintORM.id,
            SprintORM.project_id,
            SprintORM.name,
            SprintORM.status,
            SprintORM.sprint_start,
            SprintORM.sprint_end,
            SprintORM.goal,
        ).where(SprintORM.project_id.in_(project_uuids))
        if sprint_ids:
            stmt = stmt.where(SprintORM.id.in_([uuid.UUID(x) for x in sprint_ids]))
        if statuses:
            stmt = stmt.where(SprintORM.status.in_(statuses))
        if date_from:
            stmt = stmt.where(SprintORM.sprint_end >= date_from)
        if date_to:
            stmt = stmt.where(SprintORM.sprint_start <= date_to)
        stmt = _apply_sort(stmt, sort, labels=[], metric_label="count", model=SprintORM)
        # Default order if user did not specify any sort.
        if not sort:
            stmt = stmt.order_by(desc(SprintORM.sprint_start))
        if limit:
            stmt = stmt.limit(limit)
        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).mappings().all()
        return [
            {
                "id": str(r["id"]),
                "project_id": str(r["project_id"]),
                "name": r["name"],
                "status": r["status"],
                "start_date": r["sprint_start"],
                "end_date": r["sprint_end"],
                "goal": r["goal"],
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # sprint_burndown_points
    # ------------------------------------------------------------------

    async def sprint_burndown_points(
        self,
        *,
        sprint_id: str,
        workspace_id: str,
        sprint_start: date,
        sprint_end: date,
        total_tasks: int | None = None,
    ) -> list[dict[str, Any]]:
        sprint_uuid = uuid.UUID(sprint_id)
        ws_uuid = uuid.UUID(workspace_id)
        if total_tasks is None:
            async with self._session_factory() as session:
                total_result = await session.execute(
                    select(func.count())
                    .select_from(TaskORM)
                    .join(ProjectORM, TaskORM.project_id == ProjectORM.id)
                    .where(TaskORM.sprint_id == sprint_uuid)
                    .where(ProjectORM.workspace_id == ws_uuid)
                )
            total_tasks = int(total_result.scalar() or 0)

        # «Аппроксимация»: считаем completed_at по дням, накапливаем
        # closed-count и вычитаем из total. Это близко к «remaining tasks
        # at end-of-day D» при предположении что задача однажды
        # завершённая больше не вновь открывается (что верно для MVP).
        if sprint_end < sprint_start:
            return []

        # Sargable-фильтр: избегаем func.date() на completed_at,
        # чтобы PostgreSQL мог использовать индекс.
        sprint_start_dt = datetime.combine(sprint_start, time.min)
        sprint_end_dt = datetime.combine(sprint_end + timedelta(days=1), time.min)
        day_expr = func.date_trunc("day", TaskORM.completed_at)
        async with self._session_factory() as session:
            completed_rows = (
                await session.execute(
                    select(
                        day_expr.label("day"),
                        func.count().label("count"),
                    )
                    .select_from(TaskORM)
                    .join(ProjectORM, TaskORM.project_id == ProjectORM.id)
                    .where(TaskORM.sprint_id == sprint_uuid)
                    .where(TaskORM.completed_at.is_not(None))
                    .where(TaskORM.completed_at >= sprint_start_dt)
                    .where(TaskORM.completed_at < sprint_end_dt)
                    .where(ProjectORM.workspace_id == ws_uuid)
                    .group_by(day_expr)
                )
            ).all()
        completed_by_day: dict[date, int] = {}
        for row in completed_rows:
            day_value = row[0]
            if day_value is None:
                continue
            day_date = day_value.date() if hasattr(day_value, "date") else day_value
            completed_by_day[day_date] = int(row[1])

        days = (sprint_end - sprint_start).days
        if days < 0:
            return []
        # Количество интервалов = days, количество точек = days+1
        # (от sprint_start до sprint_end включительно).
        # Для 1-дневного спринта (days=0) добавляем конечную точку,
        # чтобы идеальная линия дошла до 0.
        num_points = days + 1 if days > 0 else 2
        ideal_step = total_tasks / days if days > 0 else total_tasks
        points: list[dict[str, Any]] = []
        cumulative_completed = 0
        for offset in range(num_points):
            d = sprint_start + timedelta(days=offset)
            if d in completed_by_day:
                cumulative_completed += completed_by_day[d]
            remaining = max(total_tasks - cumulative_completed, 0)
            ideal = max(round(total_tasks - ideal_step * offset, 2), 0)
            points.append(
                {
                    "date": _coerce(d),
                    "remaining_count": remaining,
                    "ideal_count": ideal,
                }
            )
        return points

    # ------------------------------------------------------------------
    # sprint_velocity
    # ------------------------------------------------------------------

    async def sprint_velocity(
        self,
        *,
        workspace_id: str,
        project_id: str,
        last_n_sprints: int = 5,
    ) -> list[dict[str, Any]]:
        project_uuid = uuid.UUID(project_id)
        ws_uuid = uuid.UUID(workspace_id)
        # Берём N последних закрытых спринтов.
        # Join с ProjectORM для гарантии изоляции workspace.
        sprints_stmt = (
            select(SprintORM.id, SprintORM.name, SprintORM.sprint_start, SprintORM.sprint_end)
            .join(ProjectORM, SprintORM.project_id == ProjectORM.id)
            .where(SprintORM.project_id == project_uuid)
            .where(ProjectORM.workspace_id == ws_uuid)
            .where(SprintORM.status == "closed")
            .order_by(desc(SprintORM.sprint_end))
            .limit(last_n_sprints)
        )
        async with self._session_factory() as session:
            sprints = (await session.execute(sprints_stmt)).mappings().all()
        if not sprints:
            return []

        sprint_ids = [s["id"] for s in sprints]

        async with self._session_factory() as session:
            total_counts = (
                await session.execute(
                    select(TaskORM.sprint_id, func.count().label("count"))
                    .where(TaskORM.sprint_id.in_(sprint_ids))
                    .group_by(TaskORM.sprint_id)
                )
            ).all()
        total_by_sprint: dict[uuid.UUID, int] = {r[0]: int(r[1]) for r in total_counts}

        # Completed counts filtered by sprint date range per the port contract.
        completed_by_sprint: dict[uuid.UUID, int] = {}
        if sprint_ids:
            completed_clauses: list[Any] = []
            for s in sprints:
                sid = s["id"]
                clause = (
                    (TaskORM.sprint_id == sid)
                    & TaskORM.completed_at.is_not(None)
                )
                if s["sprint_start"] is not None:
                    start_dt = datetime.combine(s["sprint_start"], time.min)
                    clause = clause & (TaskORM.completed_at >= start_dt)
                if s["sprint_end"] is not None:
                    end_dt = datetime.combine(s["sprint_end"] + timedelta(days=1), time.min)
                    clause = clause & (TaskORM.completed_at < end_dt)
                completed_clauses.append(clause)

            async with self._session_factory() as session:
                completed_rows = (
                    await session.execute(
                        select(TaskORM.sprint_id, func.count().label("count"))
                        .where(or_(*completed_clauses))
                        .group_by(TaskORM.sprint_id)
                    )
                ).all()
            completed_by_sprint = {r[0]: int(r[1]) for r in completed_rows}

        result: list[dict[str, Any]] = []
        # Хронология: от старых к новым.
        for s in reversed(sprints):
            sid = s["id"]
            result.append(
                {
                    "sprint_id": str(sid),
                    "sprint_name": s["name"],
                    "sprint_end": s["sprint_end"],
                    "completed_count": completed_by_sprint.get(sid, 0),
                    "total_count": total_by_sprint.get(sid, 0),
                }
            )
        return result

    # ------------------------------------------------------------------
    # project_progress_counts
    # ------------------------------------------------------------------

    async def project_progress_counts(
        self,
        *,
        workspace_id: str,
        project_ids: list[str],
        overdue_date: date | None = None,
    ) -> list[dict[str, Any]]:
        ws_uuid = uuid.UUID(workspace_id)
        project_uuids = [uuid.UUID(x) for x in project_ids]

        completed_expr = func.count(TaskORM.completed_at).label("completed_count")
        overdue_expr = func.count(
            case(
                (
                    (
                        TaskORM.completed_at.is_(None)
                        & (TaskORM.due_date < overdue_date if overdue_date else False)  # noqa: E712
                    ),
                    TaskORM.id,
                ),
            )
        ).label("overdue_count")

        stmt: Select[Any] = (
            select(
                TaskORM.project_id.label("project_id"),
                func.count().label("total_count"),
                completed_expr,
                overdue_expr,
            )
            .select_from(TaskORM)
            .join(ProjectORM, TaskORM.project_id == ProjectORM.id)
            .where(TaskORM.project_id.in_(project_uuids))
            .where(ProjectORM.workspace_id == ws_uuid)
            .group_by(TaskORM.project_id)
        )

        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).all()
        return [
            {
                "project_id": str(r[0]),
                "total_count": int(r[1] or 0),
                "completed_count": int(r[2] or 0),
                "overdue_count": int(r[3] or 0),
            }
            for r in rows
        ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _apply_count_filters(
    stmt: Select[Any],
    *,
    project_ids: list[str] | None,
    sprint_ids: list[str] | None,
    epic_ids: list[str] | None,
    assignee_ids: list[str] | None,
    status_ids: list[str] | None,
    priorities: list[str] | None,
    task_types: list[str] | None,
    statuses: list[str] | None,
    completed: bool | None,
    date_field: str | None,
    date_from: date | None,
    date_to: date | None,
) -> Select[Any]:
    if project_ids:
        stmt = stmt.where(TaskORM.project_id.in_([uuid.UUID(x) for x in project_ids]))
    if sprint_ids:
        stmt = stmt.where(TaskORM.sprint_id.in_([uuid.UUID(x) for x in sprint_ids]))
    if epic_ids:
        stmt = stmt.where(TaskORM.epic_id.in_([uuid.UUID(x) for x in epic_ids]))
    if assignee_ids:
        # assignee_ids — JSONB-массив UUID-строк. Используем jsonb-оператор @>
        # с одиночным элементом — задача попадает, если включает хотя бы
        # один из заданных пользователей. Нормализуем aid через uuid.UUID,
        # чтобы избежать невалидного JSON и гарантировать каноническую форму.
        clauses = [
            TaskORM.assignee_ids.bool_op("@>")(
                cast(json.dumps([str(uuid.UUID(aid))]), JSONB)
            )
            for aid in assignee_ids
        ]
        stmt = stmt.where(or_(*clauses))
    if status_ids:
        stmt = stmt.where(TaskORM.status_id.in_([uuid.UUID(x) for x in status_ids]))
    if priorities:
        stmt = stmt.where(TaskORM.priority.in_(priorities))
    if task_types:
        stmt = stmt.where(TaskORM.task_type.in_(task_types))
    if statuses:
        stmt = stmt.where(TaskORM.status.in_(statuses))
    if completed is True:
        stmt = stmt.where(TaskORM.completed_at.is_not(None))
    elif completed is False:
        stmt = stmt.where(TaskORM.completed_at.is_(None))
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
    labels: list[str],
    metric_label: str,
    model: type | None = None,
) -> Select[Any]:
    if not sort:
        return stmt
    is_aggregate = bool(labels)
    # Determine which group-field map to use based on the primary model.
    group_map = _GROUP_FIELD_TO_COLUMN
    if model is SprintORM:
        group_map = _SPRINT_GROUP_FIELD_TO_COLUMN
    for field, direction in sort:
        order = asc if direction.lower() == "asc" else desc
        if field == metric_label:
            if not is_aggregate:
                _logger.warning("Sort by metric ignored in non-aggregate mode", field=field)
                continue
            stmt = stmt.order_by(order(literal_column(metric_label)))
        elif field in labels:
            col = group_map.get(field)
            if col is not None:
                stmt = stmt.order_by(order(col))
            else:
                _logger.warning("Unknown group sort field ignored", field=field)
        elif not is_aggregate:
            # Fallback for non-grouped sort: only resolve against the primary
            # model — adding a column from another (un-joined) ORM would
            # cause SQLAlchemy to auto-add it to FROM and produce a
            # cartesian product.
            primary = model if model is not None else TaskORM
            col = getattr(primary, field, None)
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
