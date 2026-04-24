from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DisableAuthFactorRequest(BaseModel):
    """
    Тело запроса отключения фактора 2FA.

    Атрибуты:
        method: Метод 2FA для отключения (totp, email_code, app).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "method": "totp",
            },
        },
    )

    method: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Метод 2FA для отключения (totp, email_code, app)",
        examples=["totp"],
    )
