from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UseBackupCodeRequest(BaseModel):
    """
    Тело запроса использования резервного кода 2FA.

    Атрибуты:
        code: Резервный код в открытом виде.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "A1B2C3D4",
            },
        },
    )

    code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Резервный код 2FA в открытом виде",
        examples=["A1B2C3D4"],
    )
