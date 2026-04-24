from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class OrgRoleORM(BaseORMModel):
    """ORM-модель таблицы org_roles."""

    __tablename__ = "org_roles"

    org_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True, index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    permissions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, default="org")
