from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class SessionORM(BaseORMModel):
    """ORM-модель таблицы sessions."""

    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # DeviceInfo (embedded)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=False, default="unknown")
    os: Mapped[str | None] = mapped_column(String(100), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Network
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, default="127.0.0.1")

    # Geolocation (embedded, nullable)
    geo_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    geo_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    geo_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Session state
    is_remember_me: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    max_concurrent: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    # Timestamps
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    terminated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
