from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityCategoryResponse(BaseModel):
    """API-ответ для категории деятельности."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str | None = None
    name: str
    color: str | None = None
    is_system: bool = False
    description: str | None = None
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
