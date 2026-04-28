from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, Text, Uuid
from sqlalchemy import Table
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# Association table: Organization ↔ Owner (many-to-many)
# ---------------------------------------------------------------------------

org_owners_table = Table(
    "org_owners",
    BaseORMModel.metadata,
    Column("organization_id", ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Uuid, primary_key=True),
)


# ---------------------------------------------------------------------------
# Organization (корень агрегата)
# ---------------------------------------------------------------------------

class OrganizationORM(BaseORMModel):
    """ORM-модель таблицы organizations."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    # --- OrgPersonalization (embedded VO) ---
    pers_color_hex: Mapped[str | None] = mapped_column(String(7), nullable=True)
    pers_icon: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    pers_display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pers_custom_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # OrgBranding (nested VO inside OrgPersonalization)
    pers_branding_logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    pers_branding_favicon_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    pers_branding_custom_css: Mapped[str | None] = mapped_column(Text, nullable=True)
    pers_branding_login_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- SecurityPolicy (embedded VO) ---
    sp_require_2fa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sp_password_min_length: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    sp_session_timeout_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sp_ip_allowlist: Mapped[list | None] = mapped_column(JSON, nullable=True)
    sp_domain_restrictions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    sp_require_email_verification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # --- MembershipPolicy (embedded VO) ---
    mp_allow_invitation_links: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mp_default_role: Mapped[str] = mapped_column(String(100), nullable=False, default="member")
    mp_require_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mp_max_members: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mp_allowed_email_domains: Mapped[list | None] = mapped_column(JSON, nullable=True)
