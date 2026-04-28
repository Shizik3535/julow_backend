from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class WorkspaceORM(BaseORMModel):
    """ORM-модель таблицы workspaces."""

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    workspace_type: Mapped[str] = mapped_column(String(30), nullable=False, default="team")
    organization_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    parent_workspace_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)

    # WorkspacePersonalization → скалярные колонки
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    icon: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # WorkspaceBranding (nested in personalization) → скалярные колонки
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_css: Mapped[str | None] = mapped_column(Text, nullable=True)

    # owner_ids → JSON
    owner_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    # SecurityPolicy → скалярные колонки
    pin_code_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    password_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ip_allowlist: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    sso_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="none")
    require_2fa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    session_timeout_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    security_inherit_from_parent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # MembershipPolicy → скалярные колонки
    allow_invitation_links: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    default_role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    require_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    max_members: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allowed_email_domains: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    auto_add_from_org: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    membership_inherit_from_parent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # WorkspaceLimits → скалярные колонки
    max_projects: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ws_max_members: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_storage_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    max_file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    max_teams: Mapped[int | None] = mapped_column(Integer, nullable=True)
