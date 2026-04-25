from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddBoardColumnRequest(BaseModel):
    """Запрос на добавление колонки доски."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100, description="Название колонки")
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Цвет колонки (HEX)")
    wip_limit: int | None = Field(None, ge=1, description="WIP-лимит")
    status_mapping: str | None = Field(None, description="UUID workflow-статуса для маппинга")
