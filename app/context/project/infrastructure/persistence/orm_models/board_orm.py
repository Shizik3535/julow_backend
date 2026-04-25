from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class BoardORM(BaseORMModel):
    """ORM-модель таблицы boards."""

    __tablename__ = "boards"

    project_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, unique=True, index=True,
    )

    columns: Mapped[list[BoardColumnORM]] = relationship(
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="BoardColumnORM.order",
    )
    swimlanes: Mapped[list[SwimlaneORM]] = relationship(
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SwimlaneORM.order",
    )
    workflow_statuses: Mapped[list[WorkflowStatusORM]] = relationship(
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="WorkflowStatusORM.order",
    )
    workflow_transitions: Mapped[list[WorkflowTransitionORM]] = relationship(
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    views: Mapped[list[ProjectViewORM]] = relationship(
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    automation_rules: Mapped[list[AutomationRuleORM]] = relationship(
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BoardColumnORM(BaseORMModel):
    """ORM-модель таблицы board_columns."""

    __tablename__ = "board_columns"

    board_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    wip_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status_mapping: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    board: Mapped[BoardORM] = relationship(back_populates="columns")


class SwimlaneORM(BaseORMModel):
    """ORM-модель таблицы board_swimlanes."""

    __tablename__ = "board_swimlanes"

    board_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    group_by: Mapped[str] = mapped_column(String(30), nullable=False, default="assignee")
    group_value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    board: Mapped[BoardORM] = relationship(back_populates="swimlanes")


class WorkflowStatusORM(BaseORMModel):
    """ORM-модель таблицы board_workflow_statuses."""

    __tablename__ = "board_workflow_statuses"

    board_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="todo")

    board: Mapped[BoardORM] = relationship(back_populates="workflow_statuses")


class WorkflowTransitionORM(BaseORMModel):
    """ORM-модель таблицы board_workflow_transitions."""

    __tablename__ = "board_workflow_transitions"

    board_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    from_status_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    to_status_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger: Mapped[str | None] = mapped_column(String(50), nullable=True)
    required_permission: Mapped[str | None] = mapped_column(String(255), nullable=True)

    board: Mapped[BoardORM] = relationship(back_populates="workflow_transitions")


class ProjectViewORM(BaseORMModel):
    """ORM-модель таблицы board_views."""

    __tablename__ = "board_views"

    board_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    board: Mapped[BoardORM] = relationship(back_populates="views")


class AutomationRuleORM(BaseORMModel):
    """ORM-модель таблицы board_automation_rules."""

    __tablename__ = "board_automation_rules"

    board_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger: Mapped[str] = mapped_column(String(50), nullable=False, default="status_changed")
    action: Mapped[str] = mapped_column(String(50), nullable=False, default="send_notification")
    action_params: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    board: Mapped[BoardORM] = relationship(back_populates="automation_rules")
