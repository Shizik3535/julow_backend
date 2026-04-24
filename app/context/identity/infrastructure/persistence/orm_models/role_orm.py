from __future__ import annotations

from sqlalchemy import Boolean, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class RoleORM(BaseORMModel):
    """ORM-модель таблицы roles."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    permissions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
