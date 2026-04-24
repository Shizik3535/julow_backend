from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class ProjectRoleCreated(BaseDomainEvent):
    """Кастомная роль проекта создана."""

    project_id: str = ""
    role_name: str = ""


@dataclass(frozen=True)
class ProjectRoleUpdated(BaseDomainEvent):
    """Роль проекта обновлена."""

    project_id: str = ""
    role_name: str = ""


@dataclass(frozen=True)
class ProjectRoleDeleted(BaseDomainEvent):
    """Кастомная роль проекта удалена."""

    project_id: str = ""
    role_name: str = ""
