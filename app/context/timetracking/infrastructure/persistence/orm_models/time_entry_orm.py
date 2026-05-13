from __future__ import annotations

import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date as SaDate,
    DateTime as SaDateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# Association table: time_entry_tag_links (m2m: TimeEntry ↔ TimeEntryTag)
# ---------------------------------------------------------------------------

time_entry_tags_table = Table(
    "time_entry_tag_links",
    BaseORMModel.metadata,
    Column("time_entry_id", ForeignKey("time_entries.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("time_entry_tags.id", ondelete="CASCADE"), primary_key=True),
)


# ---------------------------------------------------------------------------
# TimeEntryTimeLogORM — детализация таймера
# ---------------------------------------------------------------------------

class TimeEntryTimeLogORM(BaseORMModel):
    """ORM-модель таблицы time_entry_time_logs."""

    __tablename__ = "time_entry_time_logs"

    time_entry_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("time_entries.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(SaDateTime(timezone=True), nullable=False)
    accumulated_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    time_entry: Mapped["TimeEntryORM"] = relationship(back_populates="time_logs")


# ---------------------------------------------------------------------------
# TimeEntryORM — корень агрегата
# ---------------------------------------------------------------------------

class TimeEntryORM(BaseORMModel):
    """ORM-модель таблицы time_entries."""

    __tablename__ = "time_entries"

    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    task_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    epic_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    timer_state: Mapped[str] = mapped_column(String(20), nullable=False, default="stopped")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)

    started_at: Mapped[datetime | None] = mapped_column(SaDateTime(timezone=True), nullable=True)
    stopped_at: Mapped[datetime | None] = mapped_column(SaDateTime(timezone=True), nullable=True)

    duration_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    entry_date: Mapped[date_type] = mapped_column(SaDate, nullable=False, index=True)

    is_billable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hourly_rate_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    hourly_rate_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)

    category_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)

    # Rounding config
    rounding_rule: Mapped[str | None] = mapped_column(String(30), nullable=True)
    rounding_apply_to: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Rejection reason (denormalised)
    rejection_reason_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejected_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(SaDateTime(timezone=True), nullable=True)

    # Дочерние сущности
    time_logs: Mapped[list[TimeEntryTimeLogORM]] = relationship(
        back_populates="time_entry",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
