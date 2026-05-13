from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class TimeEntryTagORM(BaseORMModel):
    """ORM-модель таблицы time_entry_tags."""

    __tablename__ = "time_entry_tags"

    workspace_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
