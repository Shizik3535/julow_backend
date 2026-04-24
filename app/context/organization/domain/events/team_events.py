from __future__ import annotations

from dataclasses import dataclass, field

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class TeamCreated(BaseDomainEvent):
    """Команда создана."""

    org_id: str = ""
    team_id: str = ""


@dataclass(frozen=True)
class TeamUpdated(BaseDomainEvent):
    """Команда обновлена."""

    org_id: str = ""
    team_id: str = ""
    changed_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TeamDeleted(BaseDomainEvent):
    """Команда удалена."""

    org_id: str = ""
    team_id: str = ""


@dataclass(frozen=True)
class TeamMemberAdded(BaseDomainEvent):
    """Участник добавлен в команду."""

    org_id: str = ""
    team_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class TeamMemberRemoved(BaseDomainEvent):
    """Участник удалён из команды."""

    org_id: str = ""
    team_id: str = ""
    user_id: str = ""
