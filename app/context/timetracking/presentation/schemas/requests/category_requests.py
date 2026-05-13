from __future__ import annotations

from pydantic import BaseModel, Field


class CreateActivityCategoryRequest(BaseModel):
    """Тело POST /workspaces/{ws_id}/time/categories."""

    name: str = Field(..., min_length=1, max_length=100)
    color: str | None = Field(default=None, description="HEX-цвет #RRGGBB")
    description: str | None = None


class UpdateActivityCategoryRequest(BaseModel):
    """Тело PATCH /time/categories/{category_id}."""

    name: str | None = None
    color: str | None = None
    description: str | None = None
