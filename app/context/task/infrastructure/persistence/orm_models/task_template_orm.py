from __future__ import annotations

import uuid

from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date as SaDate, DateTime as SaDateTime, ForeignKey, Integer, JSON, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# Association table: task_template_labels (many-to-many для Label VO)
# ---------------------------------------------------------------------------

task_template_labels_table = Table(
    "task_template_labels",
    BaseORMModel.metadata,
    Column("template_id", ForeignKey("task_templates.id", ondelete="CASCADE"), primary_key=True),
    Column("label_name", String(100), primary_key=True),
    Column("label_color", String(7), nullable=True),
)


# ---------------------------------------------------------------------------
# TaskTemplateORM — корень агрегата
# ---------------------------------------------------------------------------

class TaskTemplateORM(BaseORMModel):
    """ORM-модель таблицы task_templates."""

    __tablename__ = "task_templates"

    project_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # RichText → скалярные колонки
    description_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_format: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # TaskType → строка
    task_type: Mapped[str] = mapped_column(String(30), nullable=False, default="task")

    # default_custom_fields → JSON
    default_custom_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)

    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Дочерние сущности
    default_checklists: Mapped[list["TemplateChecklistORM"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


# ---------------------------------------------------------------------------
# TemplateChecklistORM
# ---------------------------------------------------------------------------

class TemplateChecklistORM(BaseORMModel):
    """ORM-модель таблицы task_template_checklists."""

    __tablename__ = "task_template_checklists"

    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_templates.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    items: Mapped[list["TemplateChecklistItemORM"]] = relationship(
        back_populates="checklist",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    template: Mapped[TaskTemplateORM] = relationship(back_populates="default_checklists")


# ---------------------------------------------------------------------------
# TemplateChecklistItemORM
# ---------------------------------------------------------------------------

class TemplateChecklistItemORM(BaseORMModel):
    """ORM-модель таблицы task_template_checklist_items."""

    __tablename__ = "task_template_checklist_items"

    checklist_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_template_checklists.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    due_date: Mapped[date | None] = mapped_column(SaDate, nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(SaDateTime(timezone=True), nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    checklist: Mapped[TemplateChecklistORM] = relationship(back_populates="items")
