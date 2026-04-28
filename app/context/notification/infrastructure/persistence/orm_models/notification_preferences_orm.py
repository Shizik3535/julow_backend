from __future__ import annotations

import uuid
from datetime import time

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Time, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class NotificationPreferencesORM(BaseORMModel):
    """ORM-модель таблицы notification_preferences."""

    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, nullable=False, unique=True, index=True,
    )

    # NotificationPolicy (embedded VO → JSON)
    policy_mandatory_types: Mapped[list | None] = mapped_column(JSON, nullable=True)
    policy_default_channels: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # DoNotDisturbSchedule (embedded entity → скалярные колонки)
    dnd_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dnd_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    dnd_end: Mapped[time | None] = mapped_column(Time, nullable=True)
    dnd_days: Mapped[list | None] = mapped_column(JSON, nullable=True)
    dnd_timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")

    # DigestConfig (embedded entity → скалярные колонки)
    digest_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    digest_frequency: Mapped[str] = mapped_column(String(20), nullable=False, default="daily")
    digest_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    digest_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    digest_timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")

    # Reminder window (hours before deadline to notify)
    reminder_window_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=24)

    # Дочерние сущности PreferenceEntry
    preference_entries: Mapped[list["PreferenceEntryORM"]] = relationship(
        back_populates="preferences",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PreferenceEntryORM(BaseORMModel):
    """ORM-модель таблицы preference_entries."""

    __tablename__ = "preference_entries"

    preferences_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notification_preferences.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False, default="global")
    scope_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)

    preferences: Mapped[NotificationPreferencesORM] = relationship(back_populates="preference_entries")
