from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SetTaskRecurrenceRequest(BaseModel):
    """Запрос на установку конфигурации повторения задачи."""

    model_config = ConfigDict(from_attributes=True)

    pattern: str = Field(
        ...,
        description="Паттерн повторения (DAILY, WEEKLY, MONTHLY, YEARLY)",
        examples=["WEEKLY"],
    )
    interval: int = Field(
        default=1,
        ge=1,
        description="Интервал повторения (каждые N единиц)",
        examples=[1],
    )
    end_date: str | None = Field(
        default=None,
        description="Дата окончания повторения (ISO)",
        examples=["2025-12-31"],
    )
    max_occurrences: int | None = Field(
        default=None,
        description="Максимальное количество повторений",
        examples=[10],
    )
