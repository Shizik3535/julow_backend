from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class OrgRoleCreated(BaseDomainEvent):
    """Кастомная роль создана."""

    org_id: str = ""
    role_name: str = ""


@dataclass(frozen=True)
class OrgRoleUpdated(BaseDomainEvent):
    """Роль обновлена."""

    org_id: str = ""
    role_name: str = ""


@dataclass(frozen=True)
class OrgRoleDeleted(BaseDomainEvent):
    """Кастомная роль удалена."""

    org_id: str = ""
    role_name: str = ""
