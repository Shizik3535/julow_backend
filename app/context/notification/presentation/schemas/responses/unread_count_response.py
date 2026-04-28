from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UnreadCountResponse(BaseModel):
    """Ответ с количеством непрочитанных уведомлений."""

    model_config = ConfigDict(from_attributes=True)

    total: int = Field(default=0, description="Общее количество непрочитанных", examples=[5])
    by_workspace: dict[str, int] = Field(
        default_factory=dict,
        description="Количество по workspace (UUID → count)",
        examples=[{"550e8400-e29b-41d4-a716-446655440000": 3}],
    )
