from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class StorageIntegrationORM(BaseORMModel):
    """ORM-модель таблицы storage_integrations."""

    __tablename__ = "storage_integrations"

    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )

    # --- Embedded StorageConfig VO ---
    sc_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="local")
    sc_endpoint: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    sc_bucket: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    sc_region: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    sc_access_key: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # --- Embedded StorageQuota VO ---
    sq_max_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sq_used_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sq_max_file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sq_allowed_extensions: Mapped[list | None] = mapped_column(JSON, nullable=True)
