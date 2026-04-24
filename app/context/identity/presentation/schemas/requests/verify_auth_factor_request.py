from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VerifyAuthFactorRequest(BaseModel):
    """
    Тело запроса проверки кода 2FA.

    Атрибуты:
        method: Метод 2FA (totp, email_code, app).
        code: Код подтверждения.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "method": "totp",
                "code": "123456",
            },
        },
    )

    method: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Метод 2FA (totp, email_code, app)",
        examples=["totp"],
    )
    code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Код подтверждения 2FA",
        examples=["123456"],
    )
