from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EnableAuthFactorRequest(BaseModel):
    """
    Тело запроса включения фактора 2FA.

    Секрет генерируется сервером автоматически (для TOTP — через TOTPPort).

    Атрибуты:
        method: Метод 2FA (totp, email_code, app).
        is_primary: Является ли основным фактором.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "method": "totp",
                "is_primary": True,
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
    is_primary: bool = Field(
        default=False,
        description="Назначить основным фактором 2FA",
    )
