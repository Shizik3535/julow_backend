from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# Association table: Department ↔ Member (many-to-many)
# ---------------------------------------------------------------------------

department_members_table = Table(
    "department_members",
    BaseORMModel.metadata,
    Column("department_id", ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Uuid, primary_key=True),
)


# ---------------------------------------------------------------------------
# Department (корень агрегата)
# ---------------------------------------------------------------------------

class DepartmentORM(BaseORMModel):
    """ORM-модель таблицы departments."""

    __tablename__ = "departments"

    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
