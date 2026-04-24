from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.workspace.domain.value_objects.workspace_type import WorkspaceType


@dataclass(frozen=True)
class WorkspaceCreated(BaseDomainEvent):
    """Workspace создан."""

    workspace_id: str = ""
    owner_id: str = ""
    name: str = ""
    organization_id: str = ""
    parent_workspace_id: str = ""
    workspace_type: WorkspaceType = WorkspaceType.TEAM


@dataclass(frozen=True)
class WorkspaceInfoChanged(BaseDomainEvent):
    """Информация workspace обновлена."""

    workspace_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class WorkspaceArchived(BaseDomainEvent):
    """Workspace архивирован."""

    workspace_id: str = ""


@dataclass(frozen=True)
class WorkspaceRestored(BaseDomainEvent):
    """Workspace восстановлен из архива."""

    workspace_id: str = ""


@dataclass(frozen=True)
class WorkspaceSuspended(BaseDomainEvent):
    """Workspace приостановлен."""

    workspace_id: str = ""
    reason: str = ""


@dataclass(frozen=True)
class WorkspaceReactivated(BaseDomainEvent):
    """Workspace реактивирован."""

    workspace_id: str = ""


@dataclass(frozen=True)
class WorkspaceDeletionRequested(BaseDomainEvent):
    """Запрос удаления workspace."""

    workspace_id: str = ""


@dataclass(frozen=True)
class OwnershipTransferred(BaseDomainEvent):
    """Владение передано."""

    workspace_id: str = ""
    old_owner_id: str = ""
    new_owner_id: str = ""


@dataclass(frozen=True)
class WorkspacePersonalizationChanged(BaseDomainEvent):
    """Персонализация workspace изменена."""

    workspace_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SecurityPolicyChanged(BaseDomainEvent):
    """Политика безопасности изменена."""

    workspace_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MembershipPolicyChanged(BaseDomainEvent):
    """Политика членства изменена."""

    workspace_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class WorkspaceLimitsChanged(BaseDomainEvent):
    """Лимиты workspace изменены."""

    workspace_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ChildWorkspaceCreated(BaseDomainEvent):
    """Дочерний workspace создан."""

    parent_workspace_id: str = ""
    child_workspace_id: str = ""
