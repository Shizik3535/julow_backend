from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ReorderPinnedItemsRequest(BaseModel):
    """
    Тело запроса переупорядочивания закреплённых элементов.

    Атрибуты:
        ordered_ids: Список target_id в желаемом порядке.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ordered_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "660e8400-e29b-41d4-a716-446655440001",
                    "770e8400-e29b-41d4-a716-446655440002",
                ],
            },
        },
    )

    ordered_ids: list[str] = Field(
        ...,
        description="Список target_id закреплённых элементов в желаемом порядке",
    )
