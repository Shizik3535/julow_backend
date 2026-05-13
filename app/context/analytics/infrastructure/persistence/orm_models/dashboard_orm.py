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


class DashboardORM(BaseORMModel):
    """ORM-модель таблицы ``analytics_dashboards``."""

    __tablename__ = "analytics_dashboards"
    __table_args__ = (
        Index("ix_analytics_dashboards_workspace", "workspace_id"),
        Index("ix_analytics_dashboards_owner", "owner_id"),
        Index(
            "ix_analytics_dashboards_workspace_default",
            "workspace_id",
            "is_default",
        ),
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_auto_refresh: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    refresh_interval_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    widgets: Mapped[list["DashboardWidgetORM"]] = relationship(
        "DashboardWidgetORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="dashboard",
        order_by="DashboardWidgetORM.order",
    )
    shares: Mapped[list["DashboardShareORM"]] = relationship(
        "DashboardShareORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="dashboard",
    )


class DashboardWidgetORM(BaseORMModel):
    """ORM-модель таблицы ``analytics_dashboard_widgets``."""

    __tablename__ = "analytics_dashboard_widgets"
    __table_args__ = (
        Index("ix_analytics_dashboard_widgets_dashboard", "dashboard_id"),
    )

    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("analytics_dashboards.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    widget_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # WidgetConfig (widget_type, query, display_params) — сериализован в JSON
    # через DTO-мэппер, чтобы избежать дублирования VO-сериализации.
    config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    size_cols: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    size_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    position_row: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_col: Mapped[int | None] = mapped_column(Integer, nullable=True)

    dashboard: Mapped["DashboardORM"] = relationship(
        "DashboardORM", back_populates="widgets"
    )


class DashboardShareORM(BaseORMModel):
    """ORM-модель таблицы ``analytics_dashboard_shares``."""

    __tablename__ = "analytics_dashboard_shares"
    __table_args__ = (
        Index("ix_analytics_dashboard_shares_dashboard", "dashboard_id"),
        Index("ix_analytics_dashboard_shares_user", "user_id"),
    )

    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("analytics_dashboards.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    access_level: Mapped[str] = mapped_column(String(16), nullable=False)
    shared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    dashboard: Mapped["DashboardORM"] = relationship(
        "DashboardORM", back_populates="shares"
    )
