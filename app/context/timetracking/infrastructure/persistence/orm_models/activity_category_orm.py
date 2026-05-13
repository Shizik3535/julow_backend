from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class ActivityCategoryORM(BaseORMModel):
    """ORM-модель таблицы activity_categories."""

    __tablename__ = "activity_categories"

    workspace_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
