from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class FolderORM(BaseORMModel):
    """ORM-модель таблицы fs_folders."""

    __tablename__ = "fs_folders"
    __table_args__ = (
        Index("ix_fs_folders_workspace", "workspace_id"),
        Index("ix_fs_folders_parent", "parent_folder_id"),
        Index("ix_fs_folders_project", "project_id"),
    )

    name: Mapped[str] = mapped_column(String(512), nullable=False)
    folder_type: Mapped[str] = mapped_column(String(32), nullable=False, default="regular")
    parent_folder_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    color: Mapped[str | None] = mapped_column(String(16), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    permissions: Mapped[list["FolderPermissionEntryORM"]] = relationship(
        "FolderPermissionEntryORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="folder",
    )


class FolderPermissionEntryORM(BaseORMModel):
    """ORM-модель таблицы fs_folder_permissions."""

    __tablename__ = "fs_folder_permissions"

    folder_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("fs_folders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    team_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    access_level: Mapped[str] = mapped_column(String(16), nullable=False)
    granted_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    folder: Mapped["FolderORM"] = relationship(
        "FolderORM", back_populates="permissions"
    )
