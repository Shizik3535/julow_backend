from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProjectRoleDTO:
    """DTO роли проекта."""

    id: str = ""
    project_id: str = ""
    name: str = ""
    permissions: list[str] = field(default_factory=list)
    is_system: bool = False
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ProjectRoleListDTO:
    """Список ролей проекта."""

    items: list[ProjectRoleDTO] = field(default_factory=list)
    total: int = 0
