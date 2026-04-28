from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# Association table: Team ↔ Member (many-to-many)
# ---------------------------------------------------------------------------

team_members_table = Table(
    "team_members",
    BaseORMModel.metadata,
    Column("team_id", ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Uuid, primary_key=True),
)


# ---------------------------------------------------------------------------
# Team (корень агрегата)
# ---------------------------------------------------------------------------

class TeamORM(BaseORMModel):
    """ORM-модель таблицы teams."""

    __tablename__ = "teams"

    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    lead_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    icon: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
