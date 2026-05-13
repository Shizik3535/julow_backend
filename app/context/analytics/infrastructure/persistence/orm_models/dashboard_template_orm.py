from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class DashboardTemplateORM(BaseORMModel):
    """ORM-модель таблицы ``analytics_dashboard_templates``.

    ``workspace_id`` обязателен для пользовательских шаблонов
    (``is_system=False``) и NULL для системных — DDD-инвариант
    проверяется в агрегате ``DashboardTemplate.__post_init__`` и
    зеркалируется CHECK-констрейнтом ниже, чтобы инвариант держался
    даже при записи в обход ORM.
    """

    __tablename__ = "analytics_dashboard_templates"
    __table_args__ = (
        Index("ix_analytics_dashboard_templates_system", "is_system"),
        Index(
            "ix_analytics_dashboard_templates_name",
            "name",
        ),
        Index(
            "ix_analytics_dashboard_templates_workspace",
            "workspace_id",
        ),
        CheckConstraint(
            "(is_system = true AND workspace_id IS NULL)"
            " OR (is_system = false AND workspace_id IS NOT NULL)",
            name="ck_analytics_dashboard_templates_workspace_scope",
        ),
    )

    workspace_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # widget_configs: list[WidgetConfig] — сериализуется как JSON-массив.
    widget_configs: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
