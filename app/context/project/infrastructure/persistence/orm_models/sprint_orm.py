from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class SprintORM(BaseORMModel):
    """ORM-модель таблицы sprints."""

    __tablename__ = "sprints"

    project_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # SprintGoal → строка
    goal: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planning")
    # DateRange → две колонки
    sprint_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    sprint_end: Mapped[date | None] = mapped_column(Date, nullable=True)

    retro: Mapped[SprintRetroORM | None] = relationship(
        back_populates="sprint",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )


class SprintRetroORM(BaseORMModel):
    """ORM-модель таблицы sprint_retros."""

    __tablename__ = "sprint_retros"

    sprint_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sprints.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    template_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sections: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    items: Mapped[list[RetroItemORM]] = relationship(
        back_populates="retro",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    sprint: Mapped[SprintORM] = relationship(back_populates="retro")


class RetroItemORM(BaseORMModel):
    """ORM-модель таблицы sprint_retro_items."""

    __tablename__ = "sprint_retro_items"

    retro_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sprint_retros.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    section_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    votes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    retro: Mapped[SprintRetroORM] = relationship(back_populates="items")
