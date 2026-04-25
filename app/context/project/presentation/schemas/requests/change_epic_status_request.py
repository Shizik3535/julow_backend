from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeEpicStatusRequest(BaseModel):
    """Запрос на изменение статуса эпика."""

    model_config = ConfigDict(from_attributes=True)

    new_status: str = Field(
        ..., description="Новый статус: open | in_progress | done | cancelled", examples=["in_progress"]
    )
