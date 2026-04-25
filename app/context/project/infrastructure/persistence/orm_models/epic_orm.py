from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class EpicORM(BaseORMModel):
    """ORM-модель таблицы epics."""

    __tablename__ = "epics"

    project_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # RichText → две колонки
    description_format: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
