from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MarkAllReadRequest(BaseModel):
    """
    Тело запроса пометки всех уведомлений как прочитанных.

    Атрибуты:
        workspace_id: ID workspace (опционально, для фильтрации).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        },
    )

    workspace_id: str | None = Field(
        default=None,
        description="ID workspace (если указан, помечаются только уведомления в этом workspace)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
