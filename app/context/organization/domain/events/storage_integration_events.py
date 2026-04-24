from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class OrgStorageAdded(BaseDomainEvent):
    """Хранилище добавлено."""

    org_id: str = ""
    storage_id: str = ""


@dataclass(frozen=True)
class OrgStorageUpdated(BaseDomainEvent):
    """Хранилище обновлено."""

    org_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class OrgStorageQuotaExceeded(BaseDomainEvent):
    """Квота хранилища превышена."""

    org_id: str = ""
