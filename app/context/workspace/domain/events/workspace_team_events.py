from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class WorkspaceTeamCreated(BaseDomainEvent):
    """Команда workspace создана."""

    workspace_id: str = ""
    team_id: str = ""


@dataclass(frozen=True)
class WorkspaceTeamUpdated(BaseDomainEvent):
    """Команда workspace обновлена."""

    workspace_id: str = ""
    team_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class WorkspaceTeamDeleted(BaseDomainEvent):
    """Команда workspace удалена."""

    workspace_id: str = ""
    team_id: str = ""


@dataclass(frozen=True)
class WorkspaceTeamMemberAdded(BaseDomainEvent):
    """Участник добавлен в команду workspace."""

    workspace_id: str = ""
    team_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class WorkspaceTeamMemberRemoved(BaseDomainEvent):
    """Участник удалён из команды workspace."""

    workspace_id: str = ""
    team_id: str = ""
    user_id: str = ""
