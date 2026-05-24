from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# UserProfile (корень агрегата)
# ---------------------------------------------------------------------------

class UserProfileORM(BaseORMModel):
    """ORM-модель таблицы user_profiles."""

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False, unique=True, index=True,
    )
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Appearance settings (embedded VO)
    theme: Mapped[str] = mapped_column(String(30), nullable=False, default="system")
    accent_color: Mapped[str] = mapped_column(String(30), nullable=False, default="#6366F1")
    custom_theme_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    custom_theme_colors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    interface_density: Mapped[str] = mapped_column(String(30), nullable=False, default="comfortable")

    # Localization settings (embedded VO)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    timezone_: Mapped[str] = mapped_column("timezone", String(60), nullable=False, default="UTC")
    date_format: Mapped[str] = mapped_column(String(30), nullable=False, default="YYYY-MM-DD")
    time_format: Mapped[str] = mapped_column(String(10), nullable=False, default="h24")
    week_start_day: Mapped[str] = mapped_column(String(10), nullable=False, default="monday")

    # Navigation settings (embedded VO)
    start_page: Mapped[str] = mapped_column(String(50), nullable=False, default="dashboard")

    # Privacy settings (embedded VO)
    profile_visibility: Mapped[str] = mapped_column(String(30), nullable=False, default="organization_only")
    online_status_visibility: Mapped[str] = mapped_column(String(30), nullable=False, default="everyone")
    activity_tracking_consent: Mapped[str] = mapped_column(String(20), nullable=False, default="granted")

    # Relationships (cascade all-delete-orphan — дочерние сущности агрегата)
    social_links: Mapped[list[SocialLinkORM]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="selectin",
    )
    pinned_items: Mapped[list[PinnedItemORM]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="selectin",
    )
    hotkeys: Mapped[list[HotkeyConfigORM]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="selectin",
    )
    sidebar_sections: Mapped[list[SidebarSectionORM]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="selectin",
    )


# ---------------------------------------------------------------------------
# SocialLink
# ---------------------------------------------------------------------------

class SocialLinkORM(BaseORMModel):
    """ORM-модель таблицы profile_social_links."""

    __tablename__ = "profile_social_links"
    __table_args__ = (
        UniqueConstraint("profile_id", "platform", name="uq_profile_social_links_platform"),
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    profile: Mapped[UserProfileORM] = relationship(back_populates="social_links")


# ---------------------------------------------------------------------------
# PinnedItem
# ---------------------------------------------------------------------------

class PinnedItemORM(BaseORMModel):
    """ORM-модель таблицы profile_pinned_items."""

    __tablename__ = "profile_pinned_items"
    __table_args__ = (
        UniqueConstraint("profile_id", "target_type", "target_id", name="uq_profile_pinned_items_target"),
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pinned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    profile: Mapped[UserProfileORM] = relationship(back_populates="pinned_items")


# ---------------------------------------------------------------------------
# HotkeyConfig
# ---------------------------------------------------------------------------

class HotkeyConfigORM(BaseORMModel):
    """ORM-модель таблицы profile_hotkey_configs."""

    __tablename__ = "profile_hotkey_configs"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    key_combination: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    profile: Mapped[UserProfileORM] = relationship(back_populates="hotkeys")


# ---------------------------------------------------------------------------
# SidebarSection
# ---------------------------------------------------------------------------

class SidebarSectionORM(BaseORMModel):
    """ORM-модель таблицы profile_sidebar_sections."""

    __tablename__ = "profile_sidebar_sections"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    section_id: Mapped[str] = mapped_column(String(100), nullable=False)
    is_collapsed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    item_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    profile: Mapped[UserProfileORM] = relationship(back_populates="sidebar_sections")
