from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class ReportORM(BaseORMModel):
    """ORM-модель таблицы ``analytics_reports``.

    `query` (AnalyticsQuery) хранится в JSONB; для эффективной фильтрации
    по `data_source` / `bounded_context` (см. ReportRepository) — продублированы
    в отдельные индексируемые колонки.
    """

    __tablename__ = "analytics_reports"
    __table_args__ = (
        Index("ix_analytics_reports_workspace", "workspace_id"),
        Index("ix_analytics_reports_owner", "owner_id"),
        Index("ix_analytics_reports_report_type", "report_type"),
        Index("ix_analytics_reports_query_data_source", "query_data_source"),
        Index(
            "ix_analytics_reports_query_bounded_context",
            "query_bounded_context",
        ),
        Index(
            "ix_analytics_reports_workspace_type",
            "workspace_id",
            "report_type",
        ),
        Index(
            "ix_analytics_reports_schedule_active",
            "schedule_is_active",
            "schedule_next_run_at",
        ),
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_type: Mapped[str] = mapped_column(String(64), nullable=False)

    # AnalyticsQuery: сериализованный VO + денормализованные индексы.
    query: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    query_data_source: Mapped[str] = mapped_column(String(64), nullable=False)
    query_bounded_context: Mapped[str] = mapped_column(String(32), nullable=False)

    # ReportSchedule встроен как набор колонок: на отчёт допустимо
    # максимум одно активное расписание, выносить в отдельную таблицу
    # ради планировщика преждевременно.
    schedule_frequency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    schedule_recipients: Mapped[list[str] | None] = mapped_column(
        JSONB, nullable=True
    )
    schedule_is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    schedule_next_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    schedule_last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    last_generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_export_format: Mapped[str | None] = mapped_column(String(16), nullable=True)

    shares: Mapped[list["ReportShareORM"]] = relationship(
        "ReportShareORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="report",
    )


class ReportShareORM(BaseORMModel):
    """ORM-модель таблицы ``analytics_report_shares``."""

    __tablename__ = "analytics_report_shares"
    __table_args__ = (
        Index("ix_analytics_report_shares_report", "report_id"),
        Index("ix_analytics_report_shares_user", "user_id"),
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("analytics_reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    access_level: Mapped[str] = mapped_column(String(16), nullable=False)
    shared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    report: Mapped["ReportORM"] = relationship("ReportORM", back_populates="shares")


class ReportJobORM(BaseORMModel):
    """ORM-модель таблицы ``analytics_report_jobs``.

    Чисто инфраструктурная сущность — отражает состояние асинхронной
    генерации отчёта (без доменного агрегата). Используется
    ``ReportGeneratorPort`` адаптером.
    """

    __tablename__ = "analytics_report_jobs"
    __table_args__ = (
        Index("ix_analytics_report_jobs_report", "report_id"),
        Index("ix_analytics_report_jobs_workspace", "workspace_id"),
        Index("ix_analytics_report_jobs_status", "status"),
        Index("ix_analytics_report_jobs_requested_by", "requested_by"),
        Index(
            "ix_analytics_report_jobs_scheduled_report",
            "scheduled_report_id",
        ),
    )

    report_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    report_type: Mapped[str] = mapped_column(String(64), nullable=False)
    query: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    format: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    download_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    estimated_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scheduled_report_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
