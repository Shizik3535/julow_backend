from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TimeEntryResponse(BaseModel):
    """API-ответ для записи времени."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    workspace_id: str
    task_id: str | None = None
    project_id: str | None = None
    epic_id: str | None = None
    description: str | None = None
    timer_state: str = "stopped"
    status: str = "draft"
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    duration_seconds: int = 0
    entry_date: str = ""
    is_billable: bool = False
    hourly_rate: dict[str, Any] | None = None
    category_id: str | None = None
    tag_ids: list[str] = []
    time_logs: list[dict[str, Any]] = []
    rejection_reason: dict[str, Any] | None = None
    rounding_config: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
