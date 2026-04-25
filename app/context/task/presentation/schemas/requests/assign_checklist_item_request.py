from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AssignChecklistItemRequest(BaseModel):
    """Запрос на назначение исполнителя пункта чек-листа."""

    model_config = ConfigDict(from_attributes=True)

    assignee_id: str = Field(
        ...,
        description="UUID исполнителя",
        examples=["user-uuid"],
    )
