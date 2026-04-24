from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# WorkspaceMembership (корень агрегата)
# ---------------------------------------------------------------------------

class WorkspaceMembershipORM(BaseORMModel):
    """ORM-модель таблицы workspace_memberships."""

    __tablename__ = "workspace_memberships"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, unique=True, index=True,
    )

    # Дочерние сущности
    members: Mapped[list[WorkspaceMemberORM]] = relationship(
        back_populates="membership",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


# ---------------------------------------------------------------------------
# WorkspaceMember (дочерняя сущность)
# ---------------------------------------------------------------------------

class WorkspaceMemberORM(BaseORMModel):
    """ORM-модель таблицы workspace_members."""

    __tablename__ = "workspace_members"

    membership_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspace_memberships.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="direct")
    invited_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    membership: Mapped[WorkspaceMembershipORM] = relationship(back_populates="members")
