from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class NotificationORM(BaseORMModel):
    """ORM-модель таблицы notifications."""

    __tablename__ = "notifications"

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, nullable=False, index=True,
    )
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True, index=True,
    )
    notification_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    channels: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # NotificationGroupKey (embedded VO → скалярные колонки)
    group_key_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    group_key_target_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    group_key_window_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
