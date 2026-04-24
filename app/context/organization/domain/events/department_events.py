from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class DepartmentCreated(BaseDomainEvent):
    """Подразделение создано."""

    org_id: str = ""
    department_id: str = ""


@dataclass(frozen=True)
class DepartmentUpdated(BaseDomainEvent):
    """Подразделение обновлено."""

    org_id: str = ""
    department_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DepartmentDeleted(BaseDomainEvent):
    """Подразделение удалено."""

    org_id: str = ""
    department_id: str = ""


@dataclass(frozen=True)
class DepartmentMemberAdded(BaseDomainEvent):
    """Участник добавлен в подразделение."""

    org_id: str = ""
    department_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class DepartmentMemberRemoved(BaseDomainEvent):
    """Участник удалён из подразделения."""

    org_id: str = ""
    department_id: str = ""
    user_id: str = ""
