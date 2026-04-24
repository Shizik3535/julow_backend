from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class OrganizationCreated(BaseDomainEvent):
    """Организация создана."""

    org_id: str = ""
    owner_id: str = ""
    name: str = ""


@dataclass(frozen=True)
class OrganizationInfoChanged(BaseDomainEvent):
    """Информация организации обновлена."""

    org_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class OrganizationSuspended(BaseDomainEvent):
    """Организация приостановлена."""

    org_id: str = ""
    reason: str = ""


@dataclass(frozen=True)
class OrganizationReactivated(BaseDomainEvent):
    """Организация реактивирована."""

    org_id: str = ""


@dataclass(frozen=True)
class OrganizationDeletionRequested(BaseDomainEvent):
    """Запрос удаления организации."""

    org_id: str = ""


@dataclass(frozen=True)
class OwnershipTransferred(BaseDomainEvent):
    """Владение передано."""

    org_id: str = ""
    old_owner_id: str = ""
    new_owner_id: str = ""


@dataclass(frozen=True)
class OrgPersonalizationChanged(BaseDomainEvent):
    """Персонализация организации изменена."""

    org_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SecurityPolicyChanged(BaseDomainEvent):
    """Политика безопасности изменена."""

    org_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MembershipPolicyChanged(BaseDomainEvent):
    """Политика членства изменена."""

    org_id: str = ""
    changed_fields: list[str] = field(default_factory=list)
