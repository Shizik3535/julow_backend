from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateTaskInfoRequest(BaseModel):
    """Запрос на обновление информации задачи."""

    model_config = ConfigDict(from_attributes=True)

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Новый заголовок",
        examples=["Updated title"],
    )
    description_content: str | None = Field(
        default=None,
        description="Контент описания",
        examples=["Detailed description"],
    )
    description_format: str | None = Field(
        default=None,
        description="Формат описания (PLAIN, MARKDOWN, HTML)",
        examples=["MARKDOWN"],
    )
    start_date: str | None = Field(
        default=None,
        description="Дата начала (ISO)",
        examples=["2025-01-15"],
    )
    due_date: str | None = Field(
        default=None,
        description="Дедлайн (ISO)",
        examples=["2025-02-01"],
    )
