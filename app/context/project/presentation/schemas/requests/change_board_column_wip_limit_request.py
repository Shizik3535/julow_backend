from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeBoardColumnWipLimitRequest(BaseModel):
    """Запрос на изменение WIP-лимита колонки."""

    model_config = ConfigDict(from_attributes=True)

    wip_limit: int | None = Field(None, ge=1, description="Новый WIP-лимит (None — без ограничения)")
