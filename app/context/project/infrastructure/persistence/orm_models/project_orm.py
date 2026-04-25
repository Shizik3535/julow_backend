from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel

# Association table: project <-> owner (many-to-many)
project_owners_table = Table(
    "project_owners",
    BaseORMModel.metadata,
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class ProjectORM(BaseORMModel):
    """ORM-модель таблицы projects."""

    __tablename__ = "projects"

    workspace_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # RichText → две колонки
    description_format: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # Category → скаляры
    category_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category_color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # Methodology (Enum → String)
    methodology: Mapped[str] = mapped_column(String(50), nullable=False, default="kanban")
    # MethodologyCapabilities → 8 boolean колонок
    has_sprints: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_backlog: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_milestones: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_epics: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_wip_limits: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_velocity: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_retros: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_burndown: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Visibility (Enum → String)
    visibility: Mapped[str] = mapped_column(String(30), nullable=False, default="private")
    # Status (Enum → String)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Дочерние entities
    milestones: Mapped[list[MilestoneORM]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    custom_field_definitions: Mapped[list[ProjectCustomFieldORM]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class MilestoneORM(BaseORMModel):
    """ORM-модель таблицы project_milestones."""

    __tablename__ = "project_milestones"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # RichText → две колонки
    description_format: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="not_started")
    due_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[ProjectORM] = relationship(back_populates="milestones")


class ProjectCustomFieldORM(BaseORMModel):
    """ORM-модель таблицы project_custom_field_definitions."""

    __tablename__ = "project_custom_field_definitions"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(30), nullable=False, default="text")
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)
    default_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[ProjectORM] = relationship(back_populates="custom_field_definitions")
