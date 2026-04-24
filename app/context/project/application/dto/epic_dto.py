from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class EpicDTO:
    """DTO эпика."""

    id: str = ""
    project_id: str = ""
    name: str = ""
    description: dict[str, Any] | None = None
    status: str = ""
    start_date: str | None = None
    due_date: str | None = None
    owner_id: str | None = None
    color: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class EpicListDTO:
    """Список эпиков."""

    items: list[EpicDTO] = field(default_factory=list)
    total: int = 0
