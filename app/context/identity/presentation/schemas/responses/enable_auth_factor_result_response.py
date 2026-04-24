from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EnableAuthFactorResultResponse(BaseModel):
    """
    Ответ с результатом включения фактора 2FA.

    Для TOTP возвращает provisioning URI для генерации QR-кода
    и Base32-секрет для ручного ввода.

    Атрибуты:
        method: Метод 2FA.
        provisioning_uri: otpauth:// URI для QR-кода (только TOTP, иначе None).
        secret: Base32-секрет (только TOTP, иначе None).
    """

    model_config = ConfigDict(from_attributes=True)

    method: str = Field(..., description="Метод 2FA", examples=["totp"])
    provisioning_uri: str | None = Field(
        default=None,
        description="otpauth:// URI для генерации QR-кода (только TOTP)",
        examples=["otpauth://totp/Julow:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Julow"],
    )
    secret: str | None = Field(
        default=None,
        description="Base32-секрет для ручного ввода (только TOTP)",
        examples=["JBSWY3DPEHPK3PXP"],
    )
