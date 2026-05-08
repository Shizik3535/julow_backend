"""filestorage_initial

Создаёт таблицы FileStorage BC:
fs_storages, fs_folders, fs_folder_permissions,
fs_files, fs_file_versions, fs_file_permissions, fs_file_tags,
fs_file_locks, fs_file_share_links.

Revision ID: f1a2b3c4d5e6
Revises: e0f1a2b3c4d5
Create Date: 2026-05-08 21:00:00.000000+00:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


revision: str = "f1a2b3c4d5e6"
down_revision: str | Sequence[str] | None = "e0f1a2b3c4d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # --- fs_storages ---
    op.create_table(
        "fs_storages",
        sa.Column("owner_type", sa.String(length=32), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("endpoint", sa.String(length=512), nullable=True),
        sa.Column("bucket", sa.String(length=256), nullable=True),
        sa.Column("region", sa.String(length=64), nullable=True),
        sa.Column("access_key_ref", sa.String(length=256), nullable=True),
        sa.Column("secret_key_ref", sa.String(length=256), nullable=True),
        sa.Column("custom_params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("max_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("used_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("allowed_file_types", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("max_file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("is_encrypted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_type", "owner_id", name="uq_fs_storages_owner_type_owner_id"),
    )
    op.create_index("ix_fs_storages_owner_id", "fs_storages", ["owner_id"])

    # --- fs_folders ---
    op.create_table(
        "fs_folders",
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("folder_type", sa.String(length=32), nullable=False, server_default="regular"),
        sa.Column("parent_folder_id", sa.Uuid(), nullable=True),
        sa.Column("color", sa.String(length=16), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(length=64), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_shared", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fs_folders_workspace", "fs_folders", ["workspace_id"])
    op.create_index("ix_fs_folders_parent", "fs_folders", ["parent_folder_id"])
    op.create_index("ix_fs_folders_project", "fs_folders", ["project_id"])

    op.create_table(
        "fs_folder_permissions",
        sa.Column("folder_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("team_id", sa.Uuid(), nullable=True),
        sa.Column("access_level", sa.String(length=16), nullable=False),
        sa.Column("granted_by", sa.Uuid(), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["folder_id"], ["fs_folders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fs_folder_permissions_folder_id", "fs_folder_permissions", ["folder_id"])

    # --- fs_files ---
    op.create_table(
        "fs_files",
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("original_name", sa.String(length=512), nullable=False),
        sa.Column("file_type", sa.String(length=32), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("mime_type", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("storage_id", sa.Uuid(), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("folder_id", sa.Uuid(), nullable=True),
        sa.Column("uploader_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("scan_status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="active"),
        sa.Column("preview_path", sa.String(length=1024), nullable=True),
        sa.Column("is_shared", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("lock_locked_by", sa.Uuid(), nullable=True),
        sa.Column("lock_locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lock_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lock_reason", sa.String(length=512), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fs_files_workspace_status", "fs_files", ["workspace_id", "status"])
    op.create_index("ix_fs_files_folder", "fs_files", ["folder_id"])
    op.create_index("ix_fs_files_storage", "fs_files", ["storage_id"])
    op.create_index("ix_fs_files_uploader", "fs_files", ["uploader_id"])
    op.create_index("ix_fs_files_owner", "fs_files", ["owner_id"])

    # --- fs_file_versions ---
    op.create_table(
        "fs_file_versions",
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("uploader_id", sa.Uuid(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["fs_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_id", "version_number", name="uq_fs_file_versions_file_version"),
    )
    op.create_index("ix_fs_file_versions_file_id", "fs_file_versions", ["file_id"])

    # --- fs_file_permissions ---
    op.create_table(
        "fs_file_permissions",
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("team_id", sa.Uuid(), nullable=True),
        sa.Column("access_level", sa.String(length=16), nullable=False),
        sa.Column("granted_by", sa.Uuid(), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["fs_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fs_file_permissions_file_id", "fs_file_permissions", ["file_id"])

    # --- fs_file_tags ---
    op.create_table(
        "fs_file_tags",
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("color", sa.String(length=16), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["fs_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_id", "name", name="uq_fs_file_tags_file_name"),
    )
    op.create_index("ix_fs_file_tags_file_id", "fs_file_tags", ["file_id"])

    # --- fs_file_locks (зарезервировано на будущее, lock хранится в fs_files) ---
    op.create_table(
        "fs_file_locks",
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("locked_by", sa.Uuid(), nullable=False),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.String(length=512), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["fs_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fs_file_locks_file_id", "fs_file_locks", ["file_id"])

    # --- fs_file_share_links ---
    op.create_table(
        "fs_file_share_links",
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("password_hash", sa.String(length=128), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("access_level", sa.String(length=16), nullable=False),
        sa.Column("allow_download", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("current_uses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("link_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["fs_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_fs_file_share_links_token"),
    )
    op.create_index("ix_fs_file_share_links_file_id", "fs_file_share_links", ["file_id"])
    op.create_index("ix_fs_file_share_links_token", "fs_file_share_links", ["token"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_fs_file_share_links_token", table_name="fs_file_share_links")
    op.drop_index("ix_fs_file_share_links_file_id", table_name="fs_file_share_links")
    op.drop_table("fs_file_share_links")

    op.drop_index("ix_fs_file_locks_file_id", table_name="fs_file_locks")
    op.drop_table("fs_file_locks")

    op.drop_index("ix_fs_file_tags_file_id", table_name="fs_file_tags")
    op.drop_table("fs_file_tags")

    op.drop_index("ix_fs_file_permissions_file_id", table_name="fs_file_permissions")
    op.drop_table("fs_file_permissions")

    op.drop_index("ix_fs_file_versions_file_id", table_name="fs_file_versions")
    op.drop_table("fs_file_versions")

    op.drop_index("ix_fs_files_owner", table_name="fs_files")
    op.drop_index("ix_fs_files_uploader", table_name="fs_files")
    op.drop_index("ix_fs_files_storage", table_name="fs_files")
    op.drop_index("ix_fs_files_folder", table_name="fs_files")
    op.drop_index("ix_fs_files_workspace_status", table_name="fs_files")
    op.drop_table("fs_files")

    op.drop_index("ix_fs_folder_permissions_folder_id", table_name="fs_folder_permissions")
    op.drop_table("fs_folder_permissions")

    op.drop_index("ix_fs_folders_project", table_name="fs_folders")
    op.drop_index("ix_fs_folders_parent", table_name="fs_folders")
    op.drop_index("ix_fs_folders_workspace", table_name="fs_folders")
    op.drop_table("fs_folders")

    op.drop_index("ix_fs_storages_owner_id", table_name="fs_storages")
    op.drop_table("fs_storages")
