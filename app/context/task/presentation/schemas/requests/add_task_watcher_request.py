from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddTaskWatcherRequest(BaseModel):
    """Запрос на добавление наблюдателя задаче."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(
        ...,
        description="UUID пользователя-наблюдателя",
        examples=["user-uuid"],
    )
