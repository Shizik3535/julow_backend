from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProjectMemberDTO:
    """DTO участника проекта."""

    id: str = ""
    user_id: str = ""
    role_id: str = ""
    joined_at: datetime | None = None
    is_active: bool = True


@dataclass
class ProjectMemberListDTO:
    """Список участников проекта."""

    items: list[ProjectMemberDTO] = field(default_factory=list)
    total: int = 0
