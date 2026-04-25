from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class ProjectMembershipORM(BaseORMModel):
    """ORM-модель таблицы project_memberships."""

    __tablename__ = "project_memberships"

    project_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, unique=True, index=True,
    )

    members: Mapped[list[ProjectMemberORM]] = relationship(
        back_populates="membership",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ProjectMemberORM(BaseORMModel):
    """ORM-модель таблицы project_members."""

    __tablename__ = "project_members"

    membership_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("project_memberships.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    role_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    membership: Mapped[ProjectMembershipORM] = relationship(back_populates="members")
