from __future__ import annotations

from app.shared.application.base_dto import BaseDTO


class EnableAuthFactorResultDTO(BaseDTO):
    """
    DTO результата включения фактора 2FA (Identity BC).

    Для TOTP возвращает provisioning URI для генерации QR-кода.

    Атрибуты:
        method: Метод 2FA.
        provisioning_uri: otpauth:// URI для QR-кода (только TOTP, иначе None).
        secret: Base32-секрет (только TOTP, иначе None).
    """

    method: str
    provisioning_uri: str | None = None
    secret: str | None = None
