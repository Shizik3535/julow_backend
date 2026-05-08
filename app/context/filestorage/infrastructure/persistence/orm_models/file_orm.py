from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class FileORM(BaseORMModel):
    """ORM-модель таблицы fs_files."""

    __tablename__ = "fs_files"
    __table_args__ = (
        Index("ix_fs_files_workspace_status", "workspace_id", "status"),
        Index("ix_fs_files_folder", "folder_id"),
        Index("ix_fs_files_storage", "storage_id"),
        Index("ix_fs_files_uploader", "uploader_id"),
        Index("ix_fs_files_owner", "owner_id"),
    )

    name: Mapped[str] = mapped_column(String(512), nullable=False)
    original_name: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    storage_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    folder_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    uploader_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scan_status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    preview_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_shared: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Lock (denormalized — single optional lock per file)
    lock_locked_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    lock_locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lock_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lock_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)

    versions: Mapped[list["FileVersionORM"]] = relationship(
        "FileVersionORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="file",
        order_by="FileVersionORM.version_number",
    )
    permissions: Mapped[list["FilePermissionEntryORM"]] = relationship(
        "FilePermissionEntryORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="file",
    )
    tags: Mapped[list["FileTagORM"]] = relationship(
        "FileTagORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="file",
    )
    share_links: Mapped[list["FileShareLinkORM"]] = relationship(
        "FileShareLinkORM",
        cascade="all, delete-orphan",
        lazy="selectin",
        back_populates="file",
    )


class FileVersionORM(BaseORMModel):
    """ORM-модель таблицы fs_file_versions."""

    __tablename__ = "fs_file_versions"
    __table_args__ = (
        UniqueConstraint("file_id", "version_number", name="uq_fs_file_versions_file_version"),
    )

    file_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("fs_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    uploader_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    file: Mapped["FileORM"] = relationship("FileORM", back_populates="versions")


class FilePermissionEntryORM(BaseORMModel):
    """ORM-модель таблицы fs_file_permissions."""

    __tablename__ = "fs_file_permissions"

    file_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("fs_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    team_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    access_level: Mapped[str] = mapped_column(String(16), nullable=False)
    granted_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    file: Mapped["FileORM"] = relationship("FileORM", back_populates="permissions")


class FileTagORM(BaseORMModel):
    """ORM-модель таблицы fs_file_tags."""

    __tablename__ = "fs_file_tags"
    __table_args__ = (
        UniqueConstraint("file_id", "name", name="uq_fs_file_tags_file_name"),
    )

    file_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("fs_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    color: Mapped[str | None] = mapped_column(String(16), nullable=True)

    file: Mapped["FileORM"] = relationship("FileORM", back_populates="tags")


class FileLockORM(BaseORMModel):
    """
    ORM-модель таблицы fs_file_locks.

    Не используется напрямую (lock хранится denormalized в fs_files),
    но определена для совместимости с возможными будущими расширениями.
    """

    __tablename__ = "fs_file_locks"

    file_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("fs_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    locked_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    locked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(512), nullable=True)


class FileShareLinkORM(BaseORMModel):
    """ORM-модель таблицы fs_file_share_links."""

    __tablename__ = "fs_file_share_links"
    __table_args__ = (
        UniqueConstraint("token", name="uq_fs_file_share_links_token"),
        Index("ix_fs_file_share_links_token", "token"),
    )

    file_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("fs_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(128), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    access_level: Mapped[str] = mapped_column(String(16), nullable=False)
    allow_download: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_uses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    link_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    file: Mapped["FileORM"] = relationship("FileORM", back_populates="share_links")
