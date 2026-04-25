from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class RetroTemplateORM(BaseORMModel):
    """ORM-модель таблицы retro_templates."""

    __tablename__ = "retro_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    sections: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
