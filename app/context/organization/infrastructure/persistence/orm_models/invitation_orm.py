from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class InvitationORM(BaseORMModel):
    """ORM-модель таблицы invitations."""

    __tablename__ = "invitations"

    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    role_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    invited_by: Mapped[uuid.UUID] = mapped_column(nullable=False)
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    approved_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    # --- Embedded InvitationToken VO ---
    link_value: Mapped[str | None] = mapped_column(String(512), nullable=True, unique=True)
    link_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    link_max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    link_used_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
