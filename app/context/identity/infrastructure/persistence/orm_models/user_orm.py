from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


user_roles_table = Table(
    "user_roles",
    BaseORMModel.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class UserORM(BaseORMModel):
    """ORM-модель таблицы users."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending_verification")
    is_email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    roles: Mapped[list["RoleORM"]] = relationship(
        secondary=user_roles_table,
        lazy="selectin",
    )
