from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


# ---------------------------------------------------------------------------
# UserAuth (корень агрегата)
# ---------------------------------------------------------------------------

class UserAuthORM(BaseORMModel):
    """ORM-модель таблицы user_auths."""

    __tablename__ = "user_auths"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(500), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships (cascade all-delete-orphan — дочерние сущности агрегата)
    auth_factors: Mapped[list[AuthFactorORM]] = relationship(
        back_populates="user_auth", cascade="all, delete-orphan", lazy="selectin",
    )
    oauth_links: Mapped[list[OAuthLinkORM]] = relationship(
        back_populates="user_auth", cascade="all, delete-orphan", lazy="selectin",
    )
    login_attempts: Mapped[list[LoginAttemptORM]] = relationship(
        back_populates="user_auth", cascade="all, delete-orphan", lazy="selectin",
    )
    trusted_devices: Mapped[list[TrustedDeviceORM]] = relationship(
        back_populates="user_auth", cascade="all, delete-orphan", lazy="selectin",
    )
    email_verifications: Mapped[list[EmailVerificationORM]] = relationship(
        back_populates="user_auth", cascade="all, delete-orphan", lazy="selectin",
    )
    backup_codes: Mapped[list[BackupCodeORM]] = relationship(
        back_populates="user_auth", cascade="all, delete-orphan", lazy="selectin",
    )


# ---------------------------------------------------------------------------
# AuthFactor
# ---------------------------------------------------------------------------

class AuthFactorORM(BaseORMModel):
    """ORM-модель таблицы auth_factors."""

    __tablename__ = "auth_factors"

    user_auth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_auths.id", ondelete="CASCADE"), nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(30), nullable=False, default="totp")
    secret_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    secret_method: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user_auth: Mapped[UserAuthORM] = relationship(back_populates="auth_factors")


# ---------------------------------------------------------------------------
# OAuthLink
# ---------------------------------------------------------------------------

class OAuthLinkORM(BaseORMModel):
    """ORM-модель таблицы oauth_links."""

    __tablename__ = "oauth_links"

    user_auth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_auths.id", ondelete="CASCADE"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user_auth: Mapped[UserAuthORM] = relationship(back_populates="oauth_links")


# ---------------------------------------------------------------------------
# LoginAttempt
# ---------------------------------------------------------------------------

class LoginAttemptORM(BaseORMModel):
    """ORM-модель таблицы login_attempts."""

    __tablename__ = "login_attempts"

    user_auth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_auths.id", ondelete="CASCADE"), nullable=False, index=True)
    ip: Mapped[str] = mapped_column(String(45), nullable=False, default="127.0.0.1")
    user_agent: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    was_successful: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    login_status: Mapped[str] = mapped_column(String(20), nullable=False, default="failed")

    user_auth: Mapped[UserAuthORM] = relationship(back_populates="login_attempts")


# ---------------------------------------------------------------------------
# TrustedDevice
# ---------------------------------------------------------------------------

class TrustedDeviceORM(BaseORMModel):
    """ORM-модель таблицы trusted_devices."""

    __tablename__ = "trusted_devices"

    user_auth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_auths.id", ondelete="CASCADE"), nullable=False, index=True)
    device_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=False, default="unknown")
    os: Mapped[str | None] = mapped_column(String(100), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ip: Mapped[str] = mapped_column(String(45), nullable=False, default="127.0.0.1")
    trusted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user_auth: Mapped[UserAuthORM] = relationship(back_populates="trusted_devices")


# ---------------------------------------------------------------------------
# EmailVerification
# ---------------------------------------------------------------------------

class EmailVerificationORM(BaseORMModel):
    """ORM-модель таблицы email_verifications."""

    __tablename__ = "email_verifications"

    user_auth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_auths.id", ondelete="CASCADE"), nullable=False, index=True)
    verification_type: Mapped[str] = mapped_column(String(50), nullable=False, default="email_confirmation")
    token_value: Mapped[str] = mapped_column(String(500), nullable=False)
    token_type: Mapped[str] = mapped_column(String(50), nullable=False, default="email_confirmation")
    token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user_auth: Mapped[UserAuthORM] = relationship(back_populates="email_verifications")


# ---------------------------------------------------------------------------
# BackupCode
# ---------------------------------------------------------------------------

class BackupCodeORM(BaseORMModel):
    """ORM-модель таблицы backup_codes."""

    __tablename__ = "backup_codes"

    user_auth_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_auths.id", ondelete="CASCADE"), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user_auth: Mapped[UserAuthORM] = relationship(back_populates="backup_codes")
