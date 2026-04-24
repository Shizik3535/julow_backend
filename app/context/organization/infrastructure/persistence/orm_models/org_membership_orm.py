from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# OrgMembership (корень агрегата)
# ---------------------------------------------------------------------------

class OrgMembershipORM(BaseORMModel):
    """ORM-модель таблицы org_memberships."""

    __tablename__ = "org_memberships"

    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )

    # Дочерние сущности
    members: Mapped[list[OrgMemberORM]] = relationship(
        back_populates="membership",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


# ---------------------------------------------------------------------------
# OrgMember (дочерняя сущность)
# ---------------------------------------------------------------------------

class OrgMemberORM(BaseORMModel):
    """ORM-модель таблицы org_members."""

    __tablename__ = "org_members"

    membership_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("org_memberships.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    invited_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    membership: Mapped[OrgMembershipORM] = relationship(back_populates="members")
