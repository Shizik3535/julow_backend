from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class WorkspaceMemberJoined(BaseDomainEvent):
    """Участник присоединился к workspace."""

    workspace_id: str = ""
    user_id: str = ""
    role_id: str = ""
    source: str = ""


@dataclass(frozen=True)
class WorkspaceMemberDisplayNameChanged(BaseDomainEvent):
    """Отображаемое имя участника изменено."""

    workspace_id: str = ""
    user_id: str = ""
    display_name: str = ""


@dataclass(frozen=True)
class WorkspaceMemberRoleChanged(BaseDomainEvent):
    """Роль участника изменена."""

    workspace_id: str = ""
    user_id: str = ""
    new_role_id: str = ""


@dataclass(frozen=True)
class WorkspaceMemberRemoved(BaseDomainEvent):
    """Участник удалён из workspace."""

    workspace_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class WorkspaceMemberDeactivated(BaseDomainEvent):
    """Участник деактивирован."""

    workspace_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class WorkspaceMemberReactivated(BaseDomainEvent):
    """Участник реактивирован."""

    workspace_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class MemberAddedFromOrganization(BaseDomainEvent):
    """Участник добавлен из организации (ACL)."""

    workspace_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class MemberInheritedFromParent(BaseDomainEvent):
    """Участник унаследован из родительского workspace."""

    workspace_id: str = ""
    user_id: str = ""
    parent_workspace_id: str = ""
