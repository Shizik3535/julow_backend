from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddChecklistRequest(BaseModel):
    """Запрос на добавление чек-листа задаче."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Заголовок чек-листа",
        examples=["Deployment checklist"],
    )
