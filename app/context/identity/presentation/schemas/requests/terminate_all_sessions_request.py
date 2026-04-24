from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TerminateAllSessionsRequest(BaseModel):
    """
    Тело запроса завершения всех сессий кроме текущей.

    Атрибуты:
        current_session_id: ID текущей сессии, которую не нужно завершать.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_session_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        },
    )

    current_session_id: str = Field(
        ...,
        description="ID текущей сессии (не будет завершена)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
