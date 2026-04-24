from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ProjectDTO:
    """
    DTO проекта — полная проекция агрегата Project.

    Все поля — примитивы. Вложенные VO → dict.
    """

    id: str = ""
    workspace_id: str | None = None
    name: str = ""
    description: dict[str, Any] | None = None
    icon: str | None = None
    color: str | None = None
    category: dict[str, Any] | None = None
    methodology: str = ""
    methodology_capabilities: dict[str, bool] = field(default_factory=dict)
    visibility: str = ""
    status: str = ""
    owner_ids: list[str] = field(default_factory=list)
    start_date: str | None = None
    deadline: str | None = None
    milestones: list[dict[str, Any]] = field(default_factory=list)
    custom_field_definitions: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ProjectListDTO:
    """Список проектов."""

    items: list[ProjectDTO] = field(default_factory=list)
    total: int = 0
