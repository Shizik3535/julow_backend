from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class ProjectMemberJoined(BaseDomainEvent):
    """Участник добавлен в проект."""

    project_id: str = ""
    user_id: str = ""
    role_id: str = ""


@dataclass(frozen=True)
class ProjectMemberRemoved(BaseDomainEvent):
    """Участник удалён из проекта."""

    project_id: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class ProjectMemberRoleChanged(BaseDomainEvent):
    """Роль участника проекта изменена."""

    project_id: str = ""
    user_id: str = ""
    new_role_id: str = ""
