from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.logging import get_logger
from app.context.workspace.application.ports.integration.outboard.workspace_analytics_provider import (
    WorkspaceAnalyticsProvider,
)
from app.context.workspace.infrastructure.persistence.orm_models.workspace_orm import WorkspaceORM

_logger = get_logger(__name__)


_SUPPORTED_GROUP_FIELDS = {"status", "workspace_type", "organization_id"}


class SqlWorkspaceAnalyticsAdapter(WorkspaceAnalyticsProvider):
    """SQL-реализация ``WorkspaceAnalyticsProvider``.

    Агрегации по таблице ``workspaces`` через SQLAlchemy. Все методы
    возвращают ``list[dict[str, Any]]`` с фиксированными ключами,
    которые умеет интерпретировать ``WorkspaceAnalyticsResolver``.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_workspaces(
        self,
        *,
        workspace_ids: list[str] | None = None,
        organization_id: str | None = None,
        statuses: list[str] | None = None,
        types: list[str] | None = None,
        group_by: list[str] | None = None,
        sort: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        if group_by:
            return await self._aggregate(
                workspace_ids=workspace_ids,
                organization_id=organization_id,
                statuses=statuses,
                types=types,
                group_by=group_by,
                sort=sort,
                limit=limit,
            )
        return await self._list_rows(
            workspace_ids=workspace_ids,
            organization_id=organization_id,
            statuses=statuses,
            types=types,
            sort=sort,
            limit=limit,
        )

    # ------------------------------------------------------------------

    async def _list_rows(
        self,
        *,
        workspace_ids: list[str] | None,
        organization_id: str | None,
        statuses: list[str] | None,
        types: list[str] | None,
        sort: list[tuple[str, str]] | None,
        limit: int | None,
    ) -> list[dict[str, Any]]:
        stmt: Select[Any] = select(
            WorkspaceORM.id,
            WorkspaceORM.name,
            WorkspaceORM.status,
            WorkspaceORM.workspace_type,
            WorkspaceORM.organization_id,
            WorkspaceORM.created_at,
        )
        stmt = self._apply_filters(
            stmt,
            workspace_ids=workspace_ids,
            organization_id=organization_id,
            statuses=statuses,
            types=types,
        )
        stmt = self._apply_sort(stmt, sort, group_columns=None)
        if limit:
            stmt = stmt.limit(limit)

        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).mappings().all()
        return [
            {
                "id": str(r["id"]),
                "name": r["name"],
                "status": r["status"],
                "workspace_type": r["workspace_type"],
                "organization_id": str(r["organization_id"]) if r["organization_id"] else None,
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    async def _aggregate(
        self,
        *,
        workspace_ids: list[str] | None,
        organization_id: str | None,
        statuses: list[str] | None,
        types: list[str] | None,
        group_by: list[str],
        sort: list[tuple[str, str]] | None,
        limit: int | None,
    ) -> list[dict[str, Any]]:
        unknown = [f for f in group_by if f not in _SUPPORTED_GROUP_FIELDS]
        if unknown:
            raise ValueError(f"Unsupported group_by fields: {unknown}")

        group_cols = [_column_for(field) for field in group_by]
        stmt: Select[Any] = select(*group_cols, func.count().label("count"))
        stmt = self._apply_filters(
            stmt,
            workspace_ids=workspace_ids,
            organization_id=organization_id,
            statuses=statuses,
            types=types,
        )
        stmt = stmt.group_by(*group_cols)
        stmt = self._apply_sort(stmt, sort, group_columns=dict(zip(group_by, group_cols, strict=True)))
        if limit:
            stmt = stmt.limit(limit)

        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).all()
        out: list[dict[str, Any]] = []
        for r in rows:
            data: dict[str, Any] = {}
            for field, value in zip(group_by, r[:-1], strict=True):
                data[field] = _coerce(value)
            data["count"] = int(r[-1])
            out.append(data)
        return out

    def _apply_filters(
        self,
        stmt: Select[Any],
        *,
        workspace_ids: list[str] | None,
        organization_id: str | None,
        statuses: list[str] | None,
        types: list[str] | None,
    ) -> Select[Any]:
        if workspace_ids:
            stmt = stmt.where(WorkspaceORM.id.in_([_uuid(x) for x in workspace_ids]))
        if organization_id:
            stmt = stmt.where(WorkspaceORM.organization_id == _uuid(organization_id))
        if statuses:
            stmt = stmt.where(WorkspaceORM.status.in_(statuses))
        if types:
            stmt = stmt.where(WorkspaceORM.workspace_type.in_(types))
        return stmt

    def _apply_sort(
        self,
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
                # plain list mode
                col = getattr(WorkspaceORM, field, None)
                if col is not None:
                    stmt = stmt.order_by(order(col))
                else:
                    _logger.warning("Unknown sort field ignored", field=field)
        return stmt


def _column_for(field: str):
    if field == "status":
        return WorkspaceORM.status
    if field == "workspace_type":
        return WorkspaceORM.workspace_type
    if field == "organization_id":
        return WorkspaceORM.organization_id
    raise ValueError(f"Unsupported group field: {field}")


def _uuid(value: str) -> uuid.UUID:
    return uuid.UUID(value)


def _coerce(value: Any) -> Any:
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value
