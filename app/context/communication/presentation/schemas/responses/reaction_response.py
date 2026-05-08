from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReactionResponse(BaseModel):
    """Ответ с данными реакции."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="UUID пользователя")
    emoji: str = Field(..., description="Unicode emoji")
    created_at: datetime | None = Field(default=None, description="Время создания (UTC)")
