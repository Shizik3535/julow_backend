from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class WorkspaceInvitationORM(BaseORMModel):
    """ORM-модель таблицы workspace_invitations."""

    __tablename__ = "workspace_invitations"

    workspace_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # InvitationToken → скалярные колонки
    token_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    token_max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_used_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    role_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    invited_by: Mapped[uuid.UUID] = mapped_column(nullable=False)
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    approved_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
