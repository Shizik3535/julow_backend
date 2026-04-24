from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions import ValidationException
from app.context.identity.domain.value_objects.two_factor_method import TwoFactorMethod


@dataclass(frozen=True)
class TwoFASecret(ValueObject):
    """
    Value Object для секрета 2FA.

    Хранит зашифрованный секрет аутентификационного фактора.
    Шифрование выполняется на уровне инфраструктуры.

    Атрибуты:
        value: Зашифрованный секрет.
        method: Метод 2FA, для которого предназначен секрет.
    """

    value: str
    method: TwoFactorMethod = TwoFactorMethod.TOTP

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationException(
                field="two_fa_secret",
                message="Секрет 2FA не может быть пустым",
            )
