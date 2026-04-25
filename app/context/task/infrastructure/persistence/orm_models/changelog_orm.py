from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import DateTime as SaDateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class ChangelogEntryORM(BaseORMModel):
    """ORM-модель таблицы changelog_entries."""

    __tablename__ = "changelog_entries"

    task_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[uuid.UUID] = mapped_column(nullable=False)
    changed_at: Mapped[datetime] = mapped_column(SaDateTime(timezone=True), nullable=False)
