from __future__ import annotations

import uuid

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Column, Date as SaDate, DateTime as SaDateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# Association table: task_labels (many-to-many для Label VO)
# ---------------------------------------------------------------------------

task_labels_table = Table(
    "task_labels",
    BaseORMModel.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("label_name", String(100), primary_key=True),
    Column("label_color", String(7), nullable=True),
)


# ---------------------------------------------------------------------------
# TaskChecklistItemORM
# ---------------------------------------------------------------------------

class TaskChecklistItemORM(BaseORMModel):
    """ORM-модель таблицы task_checklist_items."""

    __tablename__ = "task_checklist_items"

    checklist_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_checklists.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    due_date: Mapped[date | None] = mapped_column(SaDate, nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(SaDateTime(timezone=True), nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    checklist: Mapped[TaskChecklistORM] = relationship(back_populates="items")


# ---------------------------------------------------------------------------
# TaskChecklistORM
# ---------------------------------------------------------------------------

class TaskChecklistORM(BaseORMModel):
    """ORM-модель таблицы task_checklists."""

    __tablename__ = "task_checklists"

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    items: Mapped[list[TaskChecklistItemORM]] = relationship(
        back_populates="checklist",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    task: Mapped[TaskORM] = relationship(back_populates="checklists")


# ---------------------------------------------------------------------------
# TaskRelationORM
# ---------------------------------------------------------------------------

class TaskRelationORM(BaseORMModel):
    """ORM-модель таблицы task_relations."""

    __tablename__ = "task_relations"

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    related_task_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    relation_type: Mapped[str] = mapped_column(String(30), nullable=False, default="relates_to")
    created_at_rel: Mapped[datetime] = mapped_column(SaDateTime(timezone=True), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(nullable=False)

    task: Mapped[TaskORM] = relationship(back_populates="relations")


# ---------------------------------------------------------------------------
# TaskWatcherORM
# ---------------------------------------------------------------------------

class TaskWatcherORM(BaseORMModel):
    """ORM-модель таблицы task_watchers."""

    __tablename__ = "task_watchers"

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    watched_at: Mapped[datetime] = mapped_column(SaDateTime(timezone=True), nullable=False)

    task: Mapped[TaskORM] = relationship(back_populates="watchers")


# ---------------------------------------------------------------------------
# TaskAttachmentORM
# ---------------------------------------------------------------------------

class TaskAttachmentORM(BaseORMModel):
    """ORM-модель таблицы task_attachments."""

    __tablename__ = "task_attachments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    file_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(SaDateTime(timezone=True), nullable=False)

    task: Mapped[TaskORM] = relationship(back_populates="attachments")


# ---------------------------------------------------------------------------
# TaskORM — корень агрегата
# ---------------------------------------------------------------------------

class TaskORM(BaseORMModel):
    """ORM-модель таблицы tasks."""

    __tablename__ = "tasks"

    project_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    parent_task_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    epic_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    # RichText → скалярные колонки
    description_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_format: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Workflow status (opaque ID из Project BC)
    status_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    # Enum VO → строка
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="none")
    task_type: Mapped[str] = mapped_column(String(30), nullable=False, default="task")

    # assignee_ids → JSONB
    assignee_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    reporter_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    # TaskProgress → int
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # EffortEstimate → скалярные колонки
    effort_estimate_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    effort_estimate_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ActualEffort → скалярные колонки
    actual_effort_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_effort_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)

    start_date: Mapped[date | None] = mapped_column(SaDate, nullable=True)
    due_date: Mapped[date | None] = mapped_column(SaDate, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(SaDateTime(timezone=True), nullable=True)

    # custom_fields → JSONB
    custom_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)

    # TaskOrder → скалярные колонки
    order_position: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    order_column_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

    sprint_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    # TaskStatus (жизненный цикл) → строка
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # RecurrenceConfig → скалярные колонки
    recurrence_pattern: Mapped[str | None] = mapped_column(String(20), nullable=True)
    recurrence_interval: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recurrence_end_date: Mapped[date | None] = mapped_column(SaDate, nullable=True)
    recurrence_max_occurrences: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Дочерние сущности
    checklists: Mapped[list[TaskChecklistORM]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    relations: Mapped[list[TaskRelationORM]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    watchers: Mapped[list[TaskWatcherORM]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attachments: Mapped[list[TaskAttachmentORM]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
