from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TimeEntryTagResponse(BaseModel):
    """API-ответ для тега записи времени."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    name: str
    color: str | None = None
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
