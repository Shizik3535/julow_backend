from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthFactorResponse(BaseModel):
    """
    Ответ с данными фактора 2FA.

    Атрибуты:
        method: Метод 2FA (totp, email_code, app).
        is_enabled: Включён ли фактор.
        is_primary: Является ли основным.
        verified_at: Время последней верификации (UTC).
        priority: Приоритет фактора.
    """

    model_config = ConfigDict(from_attributes=True)

    method: str = Field(..., description="Метод 2FA", examples=["totp"])
    is_enabled: bool = Field(..., description="Включён ли фактор")
    is_primary: bool = Field(..., description="Является ли основным фактором")
    verified_at: datetime | None = Field(default=None, description="Время последней верификации (UTC)")
    priority: int = Field(default=0, description="Приоритет фактора", examples=[0])
