from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent


@dataclass(frozen=True)
class WorkspaceRoleCreated(BaseDomainEvent):
    """Кастомная роль workspace создана."""

    workspace_id: str = ""
    role_name: str = ""


@dataclass(frozen=True)
class WorkspaceRoleUpdated(BaseDomainEvent):
    """Роль workspace обновлена."""

    workspace_id: str = ""
    role_name: str = ""


@dataclass(frozen=True)
class WorkspaceRoleDeleted(BaseDomainEvent):
    """Кастомная роль workspace удалена."""

    workspace_id: str = ""
    role_name: str = ""
