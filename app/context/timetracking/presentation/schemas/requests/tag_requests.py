from __future__ import annotations

from pydantic import BaseModel, Field


class CreateTimeEntryTagRequest(BaseModel):
    """Тело POST /workspaces/{ws_id}/time/tags."""

    name: str = Field(..., min_length=1, max_length=100)
    color: str | None = Field(default=None, description="HEX-цвет #RRGGBB")


class UpdateTimeEntryTagRequest(BaseModel):
    """Тело PATCH /time/tags/{tag_id}."""

    name: str | None = None
    color: str | None = None


class AddTimeEntryTagRequest(BaseModel):
    """Тело POST /time-entries/{entry_id}/tags."""

    tag_id: str
