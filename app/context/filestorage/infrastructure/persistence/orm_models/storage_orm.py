from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, Boolean, Index, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class StorageORM(BaseORMModel):
    """ORM-модель таблицы fs_storages."""

    __tablename__ = "fs_storages"
    __table_args__ = (
        UniqueConstraint(
            "owner_type", "owner_id", name="uq_fs_storages_owner_type_owner_id"
        ),
    )

    owner_type: Mapped[str] = mapped_column(String(32), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)

    # StorageConfig (denormalized)
    endpoint: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bucket: Mapped[str | None] = mapped_column(String(256), nullable=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    access_key_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    secret_key_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    custom_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    max_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    used_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    allowed_file_types: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    max_file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
