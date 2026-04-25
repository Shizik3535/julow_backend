from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateOrganizationRequest(BaseModel):
    """
    Тело запроса создания организации.

    Атрибуты:
        name: Название организации.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Acme Corp",
            },
        },
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название организации",
        examples=["Acme Corp"],
    )
