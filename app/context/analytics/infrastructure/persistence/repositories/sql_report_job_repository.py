"""Infrastructure-репозиторий для ``ReportJobORM``.

``ReportJob`` — чисто инфраструктурное состояние асинхронной генерации
отчёта. Доменного агрегата/репозитория нет; этот репозиторий используется
только адаптером ``ReportGeneratorPort``.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.context.analytics.application.dto.report_dto import ReportJobDTO
from app.context.analytics.infrastructure.persistence.mappers.report_job_mapper import (
    ReportJobMapper,
)
from app.context.analytics.infrastructure.persistence.orm_models.report_orm import (
    ReportJobORM,
)


class SqlReportJobRepository:
    """SQL-репозиторий состояний заданий генерации отчётов."""

    def __init__(self, session: AsyncSession, mapper: ReportJobMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def add(
        self,
        *,
        workspace_id: str,
        report_type: str,
        format: str,
        query_payload: dict[str, Any],
        requested_by: str,
        report_id: str | None = None,
        scheduled_report_id: str | None = None,
        estimated_seconds: int | None = None,
    ) -> ReportJobDTO:
        """Создать новое задание со статусом ``pending`` и вернуть DTO."""
        orm = ReportJobORM(
            id=uuid.uuid4(),
            report_id=ReportJobMapper.parse_uuid(report_id),
            workspace_id=uuid.UUID(workspace_id),
            report_type=report_type,
            query=query_payload,
            format=format,
            status="pending",
            requested_by=uuid.UUID(requested_by),
            requested_at=datetime.now(tz=timezone.utc),
            estimated_seconds=estimated_seconds,
            scheduled_report_id=ReportJobMapper.parse_uuid(scheduled_report_id),
        )
        self._session.add(orm)
        await self._session.flush()
        return self._mapper.to_dto(orm)

    async def get_by_id(self, job_id: str) -> ReportJobDTO | None:
        try:
            job_uuid = uuid.UUID(job_id)
        except (ValueError, TypeError):
            return None
        stmt = select(ReportJobORM).where(ReportJobORM.id == job_uuid)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_dto(orm) if orm else None

    async def mark_completed(
        self,
        job_id: str,
        *,
        download_url: str | None = None,
        expires_at: datetime | None = None,
    ) -> ReportJobDTO | None:
        """Перевести задание в статус ``completed`` (вызывается из воркера)."""
        try:
            job_uuid = uuid.UUID(job_id)
        except (ValueError, TypeError):
            return None
        stmt = select(ReportJobORM).where(ReportJobORM.id == job_uuid)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        orm.status = "completed"
        orm.download_url = download_url
        orm.expires_at = expires_at
        orm.completed_at = datetime.now(tz=timezone.utc)
        await self._session.flush()
        return self._mapper.to_dto(orm)

    async def mark_failed(
        self, job_id: str, *, error_message: str
    ) -> ReportJobDTO | None:
        """Перевести задание в статус ``failed`` с описанием ошибки."""
        try:
            job_uuid = uuid.UUID(job_id)
        except (ValueError, TypeError):
            return None
        stmt = select(ReportJobORM).where(ReportJobORM.id == job_uuid)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        orm.status = "failed"
        orm.error_message = error_message
        orm.completed_at = datetime.now(tz=timezone.utc)
        await self._session.flush()
        return self._mapper.to_dto(orm)
