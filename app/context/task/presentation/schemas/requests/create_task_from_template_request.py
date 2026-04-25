from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateTaskFromTemplateRequest(BaseModel):
    """Запрос на создание задачи из шаблона."""

    model_config = ConfigDict(from_attributes=True)

    template_id: str = Field(
        ...,
        description="UUID шаблона задачи",
        examples=["template-uuid"],
    )
    reporter_id: str = Field(
        ...,
        description="UUID автора задачи",
        examples=["user-uuid"],
    )
