from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.persistence.sqlalchemy_base_orm_model import BaseORMModel


class SSOIntegrationORM(BaseORMModel):
    """ORM-модель таблицы sso_integrations."""

    __tablename__ = "sso_integrations"
    __table_args__ = (
        UniqueConstraint("org_id", "provider", name="uq_sso_integrations_org_provider"),
    )

    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    sso_url: Mapped[str] = mapped_column(String(2048), nullable=False, default="")
    certificate: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    group_mapping: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    attribute_mapping: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    email_domains: Mapped[list | None] = mapped_column(JSON, nullable=True)
    auto_provision: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_role_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    added_by: Mapped[uuid.UUID] = mapped_column(nullable=False)
