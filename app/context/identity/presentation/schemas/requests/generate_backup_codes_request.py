from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GenerateBackupCodesRequest(BaseModel):
    """
    Тело запроса генерации резервных кодов 2FA.

    Атрибуты:
        count: Количество кодов для генерации (по умолчанию 10).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "count": 10,
            },
        },
    )

    count: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Количество резервных кодов для генерации (от 1 до 20)",
        examples=[10],
    )
