from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MilestoneDTO:
    """DTO milestone проекта."""

    id: str = ""
    name: str = ""
    description: dict[str, Any] | None = None
    status: str = ""
    due_date: str | None = None
    completed_at: datetime | None = None


@dataclass
class MilestoneListDTO:
    """Список milestones."""

    items: list[MilestoneDTO] = field(default_factory=list)
    total: int = 0
