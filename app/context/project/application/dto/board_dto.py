from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class BoardDTO:
    """
    DTO доски проекта.

    Вложенные entities (columns, swimlanes, statuses, transitions,
    views, automation_rules) представлены как list[dict].
    """

    id: str = ""
    project_id: str = ""
    columns: list[dict[str, Any]] = field(default_factory=list)
    swimlanes: list[dict[str, Any]] = field(default_factory=list)
    workflow_statuses: list[dict[str, Any]] = field(default_factory=list)
    workflow_transitions: list[dict[str, Any]] = field(default_factory=list)
    views: list[dict[str, Any]] = field(default_factory=list)
    automation_rules: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
