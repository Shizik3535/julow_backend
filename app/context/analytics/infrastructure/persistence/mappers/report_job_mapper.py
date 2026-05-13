"""Маппинг ``ReportJobORM`` ↔ ``ReportJobDTO``.

ReportJob — чисто инфраструктурное состояние асинхронной генерации.
Доменного агрегата нет; маппер не наследует ``BaseMapper``, а просто
переводит ORM ↔ DTO напрямую.
"""
from __future__ import annotations

import uuid

from app.context.analytics.application.dto.report_dto import ReportJobDTO
from app.context.analytics.infrastructure.persistence.orm_models.report_orm import (
    ReportJobORM,
)


class ReportJobMapper:
    """Маппер ``ReportJobORM`` ↔ ``ReportJobDTO``."""

    def to_dto(self, orm_model: ReportJobORM) -> ReportJobDTO:
        return ReportJobDTO(
            id=str(orm_model.id),
            report_id=str(orm_model.report_id) if orm_model.report_id else None,
            report_type=orm_model.report_type,
            format=orm_model.format,
            status=orm_model.status,
            download_url=orm_model.download_url,
            expires_at=orm_model.expires_at,
            error_message=orm_model.error_message,
            requested_by=str(orm_model.requested_by),
            requested_at=orm_model.requested_at,
            completed_at=orm_model.completed_at,
            estimated_seconds=orm_model.estimated_seconds,
        )

    @staticmethod
    def parse_uuid(value: str | None) -> uuid.UUID | None:
        """Безопасно конвертирует строковый UUID в ``uuid.UUID``."""
        if value is None:
            return None
        return uuid.UUID(value)
