from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SprintDTO:
    """DTO спринта."""

    id: str = ""
    project_id: str = ""
    name: str = ""
    goal: str | None = None
    status: str = ""
    date_range: dict[str, Any] | None = None
    retro: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class SprintListDTO:
    """Список спринтов."""

    items: list[SprintDTO] = field(default_factory=list)
    total: int = 0
